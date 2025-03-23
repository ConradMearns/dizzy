#!/usr/bin/env python3
import os
import sys
import errno
from collections import defaultdict
import json
import stat
from datetime import datetime
from pathlib import Path
from fuse import FUSE, FuseOSError, Operations
from dizzy import datadir

class TagFS(Operations):
    def __init__(self, storage_dir=None, tag_db_path=None):
        self.storage_dir = storage_dir or os.path.expanduser("~/tagfs_storage")
        self.tag_db_path = tag_db_path or os.path.join(self.storage_dir, "tags.json")
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Load tag database
        self.tags = self._load_tags()
        self.files = self._load_files()
        
        # Cache for file stats
        self.stats_cache = {}
    
    def _load_tags(self):
        """Load tag database from disk"""
        if os.path.exists(self.tag_db_path):
            with open(self.tag_db_path, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {'files': {}, 'tags': {}}
        return {'files': {}, 'tags': {}}
    
    def _load_files(self):
        """Create reverse mapping of file -> tags"""
        files = defaultdict(list)
        for tag, file_list in self.tags.get('tags', {}).items():
            for filename in file_list:
                files[filename].append(tag)
        return files
    
    def _save_tags(self):
        """Save tag database to disk"""
        with open(self.tag_db_path, 'w') as f:
            json.dump(self.tags, f, indent=2)
    
    def _get_real_path(self, filename):
        """Get the real path for a file in the storage directory"""
        return os.path.join(self.storage_dir, filename)
    
    def _parse_path(self, path):
        """Parse a path into tags and filename components"""
        if path == '/':
            return [], None
        
        parts = path.strip('/').split('/')
        if len(parts) == 1:
            # This is a tag or a file at the root
            return parts[0].split('+'), None
        else:
            # This is a file within a tag directory
            tags = parts[0].split('+')
            filename = parts[-1]
            return tags, filename
    
    def _get_files_for_tags(self, tags):
        """Get all files that have all the specified tags"""
        if not tags:
            # Root directory shows all tags
            return list(self.tags.get('tags', {}).keys())
        
        result = set()
        is_first = True
        
        for tag in tags:
            if tag not in self.tags.get('tags', {}):
                return []
            
            files = set(self.tags['tags'][tag])
            if is_first:
                result = files
                is_first = False
            else:
                result &= files
        
        return list(result)

    # FUSE methods
    def getattr(self, path, fh=None):
        tags, filename = self._parse_path(path)
        
        # Cache stats for better performance
        if path in self.stats_cache:
            return self.stats_cache[path]
        
        now = int(datetime.now().timestamp())
        
        if not filename:
            # This is a directory (tag or root)
            st = {
                'st_mode': (stat.S_IFDIR | 0o755),
                'st_nlink': 2,
                'st_size': 0,
                'st_ctime': now,
                'st_mtime': now,
                'st_atime': now,
                'st_uid': os.getuid(),
                'st_gid': os.getgid()
            }
        else:
            # Check if file exists in the specified tag(s)
            if filename not in self._get_files_for_tags(tags):
                raise FuseOSError(errno.ENOENT)
            
            # Get stats from real file
            real_path = self._get_real_path(filename)
            if not os.path.exists(real_path):
                raise FuseOSError(errno.ENOENT)
            
            st = os.stat(real_path)
            st = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                      'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        
        self.stats_cache[path] = st
        return st
    
    def readdir(self, path, fh):
        tags, _ = self._parse_path(path)
        
        entries = ['.', '..']
        
        if not tags:
            # Root directory shows all tags
            entries.extend(self.tags.get('tags', {}).keys())
        else:
            # Tag directory shows all files with those tags
            entries.extend(self._get_files_for_tags(tags))
        
        return entries
    
    def read(self, path, size, offset, fh):
        tags, filename = self._parse_path(path)
        
        if not filename or filename not in self._get_files_for_tags(tags):
            raise FuseOSError(errno.ENOENT)
        
        real_path = self._get_real_path(filename)
        with open(real_path, 'rb') as f:
            f.seek(offset)
            return f.read(size)
    
    def write(self, path, data, offset, fh):
        tags, filename = self._parse_path(path)
        
        if not filename or filename not in self._get_files_for_tags(tags):
            raise FuseOSError(errno.ENOENT)
        
        real_path = self._get_real_path(filename)
        with open(real_path, 'r+b') as f:
            f.seek(offset)
            f.write(data)
        return len(data)
    
    def create(self, path, mode, fi=None):
        tags, filename = self._parse_path(path)
        
        if not filename:
            raise FuseOSError(errno.EINVAL)
        
        if not tags:
            raise FuseOSError(errno.EINVAL)  # Must specify at least one tag
        
        # Create the file
        real_path = self._get_real_path(filename)
        fd = os.open(real_path, os.O_WRONLY | os.O_CREAT, mode)
        
        # Add tags to the file
        for tag in tags:
            if tag not in self.tags['tags']:
                self.tags['tags'][tag] = []
            if filename not in self.tags['tags'][tag]:
                self.tags['tags'][tag].append(filename)
        
        # Update file -> tags mapping
        self.files[filename] = tags
        
        # Update file info
        if filename not in self.tags['files']:
            self.tags['files'][filename] = {}
        
        self._save_tags()
        return fd
    
    def unlink(self, path):
        tags, filename = self._parse_path(path)
        
        if not filename or filename not in self._get_files_for_tags(tags):
            raise FuseOSError(errno.ENOENT)
        
        # Remove file from all tag listings
        for tag in self.files.get(filename, []):
            if tag in self.tags['tags'] and filename in self.tags['tags'][tag]:
                self.tags['tags'][tag].remove(filename)
        
        # Remove from files dict
        if filename in self.files:
            del self.files[filename]
        
        # Remove from files info
        if filename in self.tags['files']:
            del self.tags['files'][filename]
        
        # Delete the actual file
        real_path = self._get_real_path(filename)
        os.unlink(real_path)
        
        self._save_tags()
        return 0
    
    # Add other required FUSE methods as needed


def main():
    # Default locations
    mountpoint = os.path.join(datadir, "tagfs_mount")
    storage_dir = os.path.join(datadir, "photos")
    
    # Create necessary directories
    os.makedirs(datadir, exist_ok=True)
    os.makedirs(storage_dir, exist_ok=True)
    os.makedirs(mountpoint, exist_ok=True)
    
    print(f"TagFS: Mounting at {mountpoint}")
    print(f"TagFS: Files stored in {storage_dir}")
    
    FUSE(TagFS(storage_dir=storage_dir), mountpoint, foreground=True)


if __name__ == "__main__":
    main()

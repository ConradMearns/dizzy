# BLOB Uploading with `Try` and `Record`


![pure blob uploading](patterns/pure_blob_uploading.excalidraw.svg)

Let _Try `A`_ be our Upload policy:

```
IF `A` ENDED EXISTS: EXIT

TRY:
    UPLOAD `A`
    EMIT (RECORD `A` ENDED)
EXCEPT ...:
    IF RETRY_COUNT == 0: EMIT (RECORD `A` FAILED)
    ELSE: EMIT (RETRY `A`, RETRY_COUNT - 1)
```

# Record



# Try


## Releasing to pypi

* update CHANGELOG.md
* increment version in `__init__.py`
* push to master (via PR)
* `git tag versionCode`
* `git push origin versionCode`

* Use uv for build and upload:
    - https://docs.astral.sh/uv/

```bash
uv build
```
* use `__token__` for username and a token for password

* Test upload to Test pypi with uv:

```bash
uv publish --publish-url https://test.pypi.org/legacy/ dist/*whl
```

* Release to Official pypi with uv:

```bash
uv publish --publish-url https://upload.pypi.org/legacy/ dist/*whl
```

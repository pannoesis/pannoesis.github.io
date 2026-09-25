# Pannoesis Journal

A small static blog published at https://pannoesis.github.io/. The first post lives in `posts/neuro-symbolic-agents.md`.

To rebuild after editing the Markdown:

```sh
python3 -m pip install -r requirements.txt
python3 build.py
python3 -m unittest test_build.py
```

GitHub Pages serves the generated HTML directly from the repository root.

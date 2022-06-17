# Poetry StickyWheel Plugin

<p class="lead">
A poetry plugin to pin version dependencies when building packages with local folder dependencies.
</p>

## 🛠 Installing

```
poetry self add poetry-stickywheel-plugin
```

## 📚 Help

This plugin will rewrite folder dependencies in your poetry projects dependencies with version dependencies.

The version will be extracted from the dependencies pyproject.toml and applied as a semver match.

Assuming a `pyproject.toml` such as:

```
[tool.poetry]
name = "a"
version = "0.1.0"
description = ""
authors = []
readme = "README.md"

[tool.poetry.dependencies]
b = {path = "../b", develop = true}
```

and the dependency `pyproject.toml`

```
[tool.poetry]
name = "b"
version = "1.2.3"
description = ""
authors = []
readme = "README.md"
```

the dependency will be rewritten as if it had been defined as:

```
b = "^1.2.3"
```

## ⚖️ Licence

This project is licensed under the [MIT licence][mit_licence].

All documentation and images are licenced under the 
[Creative Commons Attribution-ShareAlike 4.0 International License][cc_by_sa].

## 📝 Meta

This project uses [Semantic Versioning][semvar].

[discussions]: https://github.com/artisanofcode/poetry-stickywheel-plugin/discussions
[mit_licence]: http://dan.mit-license.org/
[cc_by_sa]: https://creativecommons.org/licenses/by-sa/4.0/
[semvar]: http://semver.org/
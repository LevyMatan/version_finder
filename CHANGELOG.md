## [3.2.1](https://github.com/LevyMatan/version_finder/compare/v3.2.0...v3.2.1) (2024-06-30)


### Bug Fixes

* **ci:** When a single platform build fails, continue with others. ([49012d5](https://github.com/LevyMatan/version_finder/commit/49012d54c003942abdb9c18a90db4d74bc0fd601))
* linux packaging command ([d75c076](https://github.com/LevyMatan/version_finder/commit/d75c0764d56a5ef2570d442ef08e43dd4a4db4d8))

# [3.2.0](https://github.com/LevyMatan/version_finder/compare/v3.1.0...v3.2.0) (2024-06-30)


### Features

* Update icons for macOS and Linux platforms ([f899d0b](https://github.com/LevyMatan/version_finder/commit/f899d0b527e64296199270c66a852374062c0a66))

# [3.1.0](https://github.com/LevyMatan/version_finder/compare/v3.0.0...v3.1.0) (2024-06-28)


### Bug Fixes

* Remove unused mainWindow.versionFinder property ([a1c7404](https://github.com/LevyMatan/version_finder/commit/a1c74049e0b09d1a106cf53f849fb0c6dde98d0d))


### Features

* **core:** Store repo state, if any checkout occures, the state is restored ([3f41f6b](https://github.com/LevyMatan/version_finder/commit/3f41f6bb6887bbb97d12c2e98920407828412d09))

# [3.0.0](https://github.com/LevyMatan/version_finder/compare/v2.1.5...v3.0.0) (2024-06-27)


### Bug Fixes

* Add test.txt file with "Hello World!" content ([a78c10a](https://github.com/LevyMatan/version_finder/commit/a78c10ae4a1baacdd73698dcc1791aba458e9e73))
* **submodule-list:** handle empty list in renderer ([4bfb415](https://github.com/LevyMatan/version_finder/commit/4bfb415717d86347eefd68e5ef6e1bb21d079727))
* **submodules list:** return empty list when no submodules ([16e7675](https://github.com/LevyMatan/version_finder/commit/16e7675e11705f0161d3b3847b6cce29f764428a))
* **test:** modify an existing file instead of creating a new file ([4244c37](https://github.com/LevyMatan/version_finder/commit/4244c3760a22df27b89633fc95408db25c75f55a))
* **test:** reorder changing files to git init ([ab00b5d](https://github.com/LevyMatan/version_finder/commit/ab00b5dd02af05da0864bc674fbcd8f28fecd6e7))
* **test:** rewrite the file ([acbbd9b](https://github.com/LevyMatan/version_finder/commit/acbbd9bae902a6862998f436852c89639f9ad7eb))


### Features

* **core:** Add snapshot mechanisim for dirty repos ([c015bc8](https://github.com/LevyMatan/version_finder/commit/c015bc8764b61e36bd7ba89c48d76e2ec22a4350))


### BREAKING CHANGES

* **submodules list:** Instead returning a list with the value: "No submodules in Repo"
return an empty list
* **core:** The change introduced will stash any changes and save the current commit hash. After it finishes the operations, it restores all.

## [2.1.5](https://github.com/LevyMatan/version_finder/compare/v2.1.4...v2.1.5) (2024-06-26)


### Bug Fixes

* **ci:** adjust the upload file path ([af1a721](https://github.com/LevyMatan/version_finder/commit/af1a721906f479f5d268a48d4d5c99a3623f0dc6))

## [2.1.4](https://github.com/LevyMatan/version_finder/compare/v2.1.3...v2.1.4) (2024-06-26)


### Bug Fixes

* **ci:** Split release-and-build workflow ([b08835d](https://github.com/LevyMatan/version_finder/commit/b08835d91a60dae5607f07fb0a570779f0974215))

## [2.1.3](https://github.com/LevyMatan/version_finder/compare/v2.1.2...v2.1.3) (2024-06-26)


### Bug Fixes

* **ci:** Attach assets when a new Version commit is created ([fbd2c19](https://github.com/LevyMatan/version_finder/commit/fbd2c192ea5f031b51cf1c94230ebecc05f08abd))

## [2.1.2](https://github.com/LevyMatan/version_finder/compare/v2.1.1...v2.1.2) (2024-06-26)


### Bug Fixes

* **ci:** Disable the "Release" workflow ([3f8a9b6](https://github.com/LevyMatan/version_finder/commit/3f8a9b6cc5463c5796c2f11cde05bfe89138ca5f))
* **lint:** Add jest and bootstrap globals ([e513cae](https://github.com/LevyMatan/version_finder/commit/e513cae7da7b5d2a678b0467af6c3b4a61d49854))
* Update VersionFinder constructor to use dynamic branch for validation ([51835c2](https://github.com/LevyMatan/version_finder/commit/51835c250598b9ec84895d1aac527288dc6f32bf))

## [2.1.1](https://github.com/LevyMatan/version_finder/compare/v2.1.0...v2.1.1) (2024-06-25)


### Bug Fixes

* Update .releaserc message format ([3753ea5](https://github.com/LevyMatan/version_finder/commit/3753ea5c56d966b1c3105f55f7616e04fb56efec))

# [2.1.0](https://github.com/LevyMatan/version_finder/compare/v2.0.0...v2.1.0) (2024-06-25)


### Bug Fixes

* **main:** import the version finder class ([b1a443c](https://github.com/LevyMatan/version_finder/commit/b1a443c874690e9d1a5afbe00653bf2ef3accb17))


### Features

* Add check for uncommitted changes in VersionFinder initialization ([52a9f85](https://github.com/LevyMatan/version_finder/commit/52a9f85c01770aa3e331602dbaead4e3dadfa0c9))
* Add validation for search pattern in VersionFinder ([44e7438](https://github.com/LevyMatan/version_finder/commit/44e7438e5d8e202b3cc1e2b674fed2a2f9638ac5))
* **lint:** Add eslint ([e8b4920](https://github.com/LevyMatan/version_finder/commit/e8b4920b376d2b76042027b45c3ad30957743114))
* **version-finder:** Initialize VersionFinder in the constructor to set the 'isInitialized' flag to false. This ensures that the VersionFinder object is properly initialized before any method is called that relies on its initialization state. ([27f4750](https://github.com/LevyMatan/version_finder/commit/27f475036625f65ab33feddd4578a441feadea61))

# [2.0.0](https://github.com/LevyMatan/version_finder/compare/v1.1.0...v2.0.0) (2024-06-22)


* pref(ipc-comm)!: Improve preformance by changing the ipc communication. ([75609cb](https://github.com/LevyMatan/version_finder/commit/75609cbdecac9092eb052773ad8b95b75a88143f))


### BREAKING CHANGES

* The change in IPC (modyfing existing IPC) may break competability with imaginary third parties.

# [1.1.0](https://github.com/LevyMatan/version_finder/compare/v1.0.0...v1.1.0) (2024-06-22)


### Bug Fixes

* **logging:** remove the log file from repo ([0c3aa76](https://github.com/LevyMatan/version_finder/commit/0c3aa766f49747e5fa3bfda74b1b6333d626019a))


### Features

* **logging:** Add logger - with control through settings ([11988e0](https://github.com/LevyMatan/version_finder/commit/11988e0f2be18c82d2c1c90d38a26bd07111b7fa))
* **logging:** Add open log file button at settings page ([3771f54](https://github.com/LevyMatan/version_finder/commit/3771f54a09f08c5f62423500170d216113106ff2))

# 1.0.0 (2024-06-21)


### Bug Fixes

* adjust the file path ([cf1feb0](https://github.com/LevyMatan/version_finder/commit/cf1feb05297d18bf1e02f1445575904a891568a0))
* **ci:** Add github token to semantic-release ([bcce626](https://github.com/LevyMatan/version_finder/commit/bcce62639fc2ed33b0f7c56e9a04318bb09e1bdb))
* **ci:** npm version on github runner ([8c5feb3](https://github.com/LevyMatan/version_finder/commit/8c5feb301c0c468928a2d20f2972725632bbcec0))
* **ci:** pass GH_TOKEN instead of GITHUB_TOKEN ([5a90496](https://github.com/LevyMatan/version_finder/commit/5a904960693a022c064f3c9e2c8496d17854bd7d))
* Clear branch and submodule input fields in resetForm function ([326e24d](https://github.com/LevyMatan/version_finder/commit/326e24d60aef96309ac7f6dfb40add56248a7b51))
* submodules names ([c5bdffd](https://github.com/LevyMatan/version_finder/commit/c5bdffd8c1e534a4d0c3da068aa3e42653cedd5f))


### Features

* Add conditional check for valid first commit in findFirstCommit function ([9df719b](https://github.com/LevyMatan/version_finder/commit/9df719b767dfbd689e5c242f053600d06617dbea))
* Add error alert placeholder to index.html ([d89680c](https://github.com/LevyMatan/version_finder/commit/d89680c8a5cf9e5e876afdc266bc659616c0c3ed))
* Add settings button to index.html and create settings.html and settings.js files ([0fd896c](https://github.com/LevyMatan/version_finder/commit/0fd896c44a2e8b1fdfb638d3b451e2a344462c42))
* **ci:** Add versioning workflow ([a6be5fe](https://github.com/LevyMatan/version_finder/commit/a6be5fe2036dce0de4e49bfae566444469176f82))
* Update search pattern in version finder to use selected option ([c27121c](https://github.com/LevyMatan/version_finder/commit/c27121c23d785428c1c22510e8821a5c940f3375))
* **versioning:** Add semantic release ([137fd5a](https://github.com/LevyMatan/version_finder/commit/137fd5ab3200123b71e203f05ab76d191a904722))

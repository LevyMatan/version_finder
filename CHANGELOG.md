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

# CHANGELOG


## v5.6.0 (2024-12-01)

### Features

* feat: :page_facing_up: Add MIT license ([`e1c0666`](https://github.com/LevyMatan/version_finder/commit/e1c06660cb1dcbc222bd03e57254c343618e1d09))


## v5.5.1 (2024-12-01)

### Bug Fixes

* fix(GUI): :package: Add icon asset to the package ([`7a110bc`](https://github.com/LevyMatan/version_finder/commit/7a110bc296dd643f48d46322ac164187291b9b19))

### Code Style

* style(GUI): :art: remove comments ([`d60491d`](https://github.com/LevyMatan/version_finder/commit/d60491d41d779e67c59b7695e0ec2453b29758f1))


## v5.5.0 (2024-12-01)

### Features

* feat(core): :test_tube: Increase the version string finding ([`660db71`](https://github.com/LevyMatan/version_finder/commit/660db71086a303e94f70d5eb497d8d398b636947))


## v5.4.3 (2024-12-01)

### Bug Fixes

* fix(GUI): :lipstick: Make the App window bigger ([`ddd2e14`](https://github.com/LevyMatan/version_finder/commit/ddd2e14ebfac76da7171b504fe1529d3e56f142c))


## v5.4.2 (2024-12-01)

### Bug Fixes

* fix(core): :ambulance: check for ancestor return value

The most annoying --is-ancestor will return an error when the first commit is not the ancestor of the second commit. When it is, it will return an empty BYTEs string! ([`a02ac0d`](https://github.com/LevyMatan/version_finder/commit/a02ac0d789f32ee71fa2b71a138ebee929eefb89))

### Testing

* test(RepoGenerator): :poop: make the test repo with submodule ([`083cf16`](https://github.com/LevyMatan/version_finder/commit/083cf16f3eaf4307ebed6f1193124cc766376d5e))


## v5.4.1 (2024-12-01)

### Bug Fixes

* fix(GUI): don't convert string to SHA in the search function

When evoking Search in the GUI, it first tries to convert a rational string to commit SHA. The issue is when a submodule is given, the conversion is not done with respect to it ([`90e8bbf`](https://github.com/LevyMatan/version_finder/commit/90e8bbfca7fd65587adc60760e13ffdfdc8e4fd7))


## v5.4.0 (2024-11-30)

### Bug Fixes

* fix(GUI): :bug: Correctly collapse the sidebar ([`ba350e6`](https://github.com/LevyMatan/version_finder/commit/ba350e62f114c28c945c181a31ac0cfe5129932c))

### Features

* feat(GUI): :sparkles: Add sidebar with task change ability

Still need to fix the collapse button ([`eba1065`](https://github.com/LevyMatan/version_finder/commit/eba1065c02d9821067e1173f6f8f85a6a233d613))

* feat(GUI): :sparkles: Add place holder to entry fields ([`d21fdfa`](https://github.com/LevyMatan/version_finder/commit/d21fdfa60caee4231e11892a51e9caf053d33043))


## v5.3.1 (2024-11-30)

### Bug Fixes

* fix(core): Error handling at: get_commit_sha_from_relative_string

If the input commit sha is invalid, return a InvalidCommitError ([`196beb4`](https://github.com/LevyMatan/version_finder/commit/196beb4aa145e237c055c3af4379b19fe8b27791))


## v5.3.0 (2024-11-29)

### Chores

* chore(Tests): Add type annotations to test ([`2803050`](https://github.com/LevyMatan/version_finder/commit/2803050189c88a20cc8cda562a15257eae292cd0))

* chore(Infra): :bricks: fix the pyproject.toml configurations

the exclude given a list instead of a comma separated string ([`d39e8e9`](https://github.com/LevyMatan/version_finder/commit/d39e8e945434e856e77e71dcd337c8c0aba3abbf))

* chore(core): :recycle: Move git operation to a git executer class ([`c868f50`](https://github.com/LevyMatan/version_finder/commit/c868f50faeb4aeefc0d94d5ef953c0110087539a))

### Code Style

* style: :art: apply format ([`6893c37`](https://github.com/LevyMatan/version_finder/commit/6893c37d1317a34a7e65088ecc0ac769110884ab))

* style: :art: apply autopep8 ([`532cb4f`](https://github.com/LevyMatan/version_finder/commit/532cb4ffd0cead93c221a5863be692f2d1090d29))

### Features

* feat(core): :goal_net: improve error handling in VersionFinder ([`2103188`](https://github.com/LevyMatan/version_finder/commit/2103188258cfee2e4e8ced72e71962cd9bfb34a7))

* feat(ErrorHandling): :technologist: Git installation instruction when does not exist ([`2d29ad7`](https://github.com/LevyMatan/version_finder/commit/2d29ad7b3bf7ab63328a62f9f0e33f1a5715b832))

* feat(GitExecuter): :sparkles: verify git installation ([`bd4f584`](https://github.com/LevyMatan/version_finder/commit/bd4f584a1d134d445c68d3adb26b9ef27e263f1d))


## v5.2.3 (2024-11-28)

### Bug Fixes

* fix(core): :ambulance: change --is-ancestor to tun in submodule context

During the binary search to find the first commit in main repository to include a submodule commit, the comparison criteria which is --is-ancestor didn't run in the correct contect ([`b833423`](https://github.com/LevyMatan/version_finder/commit/b8334237c2e4ef584bcfbf6ecc365e62b18bd430))


## v5.2.2 (2024-11-28)

### Bug Fixes

* fix(core): :bug: more robust version pattern matching

Use the --extended-regex option in git --grep to allow more accurate detection of versions ([`9dcaffa`](https://github.com/LevyMatan/version_finder/commit/9dcaffa4dff6a2ec3df142e029c275de9a870e4f))

### Unknown

* Merge pull request #61 from LevyMatan/cli_gui_support

Cli gui support ([`d46bb5e`](https://github.com/LevyMatan/version_finder/commit/d46bb5e0deb85d6625882a2d9e4769dac026414d))


## v5.2.1 (2024-11-27)

### Bug Fixes

* fix(core): :bug: get commit between version with submodule

Correct the git command sent once there is submodule involved ([`8530821`](https://github.com/LevyMatan/version_finder/commit/853082141ca5383c954dc986c48da300e1f2fba8))

* fix(core): :ambulance: boolean opeartion on a list even if with empty string return True.

Fixed the logic of handling an empty list when searching for commits ([`24eb707`](https://github.com/LevyMatan/version_finder/commit/24eb7078f9b2b1d7e0c8e4bbf558e03813c8f1be))

### Testing

* test(core): :white_check_mark: add test to commit between versions method ([`d6f794d`](https://github.com/LevyMatan/version_finder/commit/d6f794dd72bda82134099d275cf7d904b3ec545a))

### Unknown

* Merge pull request #60 from LevyMatan/cli_gui_support

Cli gui support ([`4fd1c05`](https://github.com/LevyMatan/version_finder/commit/4fd1c054c129be0a7f96ba57ca81d9cc9157a893))


## v5.2.0 (2024-11-27)

### Bug Fixes

* fix(gui): adjust font size and entry width ([`e54ae90`](https://github.com/LevyMatan/version_finder/commit/e54ae906b755f44edd7a7212b4d157c0bdc90246))

* fix(find_first_version_containing_commit): remove branch input ([`7d7b135`](https://github.com/LevyMatan/version_finder/commit/7d7b135866d3ef0820a8799ac7eda2f7b309ed90))

### Documentation

* docs(readme): Add latestest release link and installation instruction ([`78a6cf7`](https://github.com/LevyMatan/version_finder/commit/78a6cf70ee796ea8e1afb432233446c0d52a4e03))

### Features

* feat(cli): improve command line interface

Add colors to prompts, to attract user for current selection
More elegant and easy to choose
Better completion to enter repository path ([`e394b2f`](https://github.com/LevyMatan/version_finder/commit/e394b2fb2a7e0485a7e8e870f01aa8159395bb8f))

* feat(cli): when searching for text, ask for optional submodule

Also make the autocompleter match from middle ([`087b1e7`](https://github.com/LevyMatan/version_finder/commit/087b1e723933c9adfe415d83a719ec33f667136e))

### Unknown

* Merge pull request #59 from LevyMatan/cli_gui_support

Cli gui support ([`f37ecb5`](https://github.com/LevyMatan/version_finder/commit/f37ecb54b6c1f25b4ff3a45ee7c77791c615ca78))


## v5.1.0 (2024-11-27)

### Features

* feat(package): build a package in CI for each release ([`77cde95`](https://github.com/LevyMatan/version_finder/commit/77cde9557f1861a82e5b328cea51d36be8cb814f))


## v5.0.0 (2024-11-27)

### Breaking

* feat(search by text): Add search within a submodule

BREAKING CHANGE: change the task paramter interface, removed the branch param ([`bed7c24`](https://github.com/LevyMatan/version_finder/commit/bed7c243899614abbc7d24d0c58c14c70e0a86c2))

### Documentation

* docs(API): Update description of tasks ([`cf100b4`](https://github.com/LevyMatan/version_finder/commit/cf100b429445f2f62e6f2e32f1d7ec97e8c81ba9))

### Features

* feat(cov): Upload coverage report ([`cdbd6f6`](https://github.com/LevyMatan/version_finder/commit/cdbd6f68a14b45100373838c5cbccef1c3327081))

### Unknown

* Merge pull request #58 from LevyMatan/core-impro

Core improvements ([`3c35e59`](https://github.com/LevyMatan/version_finder/commit/3c35e59fd393b37de90faabd91c1b8898da3136f))

* tests(uint): find_commits_by_text ([`6365eba`](https://github.com/LevyMatan/version_finder/commit/6365eba175fb7accf62b9ddf291e8c272109b477))


## v4.0.0 (2024-11-27)

### Breaking

* fix(version): trigger a major bump

BREAKING CHANGE: last PR had an error in the commit message which caused the major version not to increament. ([`ca69f3b`](https://github.com/LevyMatan/version_finder/commit/ca69f3b487f94b365a9d29d41c5f9a2edbf86921))


## v3.5.0 (2024-11-27)

### Bug Fixes

* fix(core): fix binary search over the submodule pointers

- Add debug for the search
- Correct the logic, adjust the is_ancestor criteria ([`d59ef68`](https://github.com/LevyMatan/version_finder/commit/d59ef6854513c887b659b4cae856aee9513ce53f))

* fix(get_commit_surrounding_versions): find the version even if the commit is the version

When searching for the next version commit, make sure to include the current commit in the search ([`83c9b0b`](https://github.com/LevyMatan/version_finder/commit/83c9b0b6e8b13608ca462aa5880a860dbdbaf86d))

* fix(gui): remove call to branch in find version API ([`708d386`](https://github.com/LevyMatan/version_finder/commit/708d3868e7aed43c824f3fcdd67110f1af63aa5e))

### Code Style

* style(core): remove extra ident ([`ba81951`](https://github.com/LevyMatan/version_finder/commit/ba81951fd64384d052016d6eac98f7e1002f57f1))

### Features

* feat(gui): file dialog box deafult is current dir ([`65b46c0`](https://github.com/LevyMatan/version_finder/commit/65b46c0b2626aae6132368688a21da04221e823a))

* feat(gui): Update repo on branch selection

BREAKING CHANGE This change solve the misalignment with the core change which require the version finder instance to update the repo before sending tasks ([`b60ff56`](https://github.com/LevyMatan/version_finder/commit/b60ff561a7bb2b2143e9312a40b77ca5b20bbff1))

* feat(gui): Add logger to the gui ([`324f505`](https://github.com/LevyMatan/version_finder/commit/324f50526237bf57d149532dd5e475303ea96e0c))

### Refactoring

* refactor(cli): remove unused import ([`d35b987`](https://github.com/LevyMatan/version_finder/commit/d35b98763421832cf2ce821e95c8e6a509ee81b7))

### Unknown

* Merge pull request #53 from LevyMatan/gui-fixes

Gui fixes ([`819ea4a`](https://github.com/LevyMatan/version_finder/commit/819ea4aaa4b930faebd20a38cc63559f2a346548))

* misc(debug): Add GUI debug configuration ([`a33c7b6`](https://github.com/LevyMatan/version_finder/commit/a33c7b67a3186c7125789e73f75409c6b96be3bd))


## v3.4.1 (2024-11-26)

### Bug Fixes

* fix(core): fix getting the next version ([`3be55e9`](https://github.com/LevyMatan/version_finder/commit/3be55e998c2b40c7a32402f1c626d226d8c30036))

### Chores

* chore(debug): remove unused configuration ([`c1186a9`](https://github.com/LevyMatan/version_finder/commit/c1186a942651b6d48486d48b945d23a4619a5ae5))


## v3.4.0 (2024-11-26)

### Features

* feat(branch): dont update repo to branch on each api

BREAKING CHANGE Now the user is required to call updated_repository
with a branch as an input in-order to call task APIs ([`b4bf5a9`](https://github.com/LevyMatan/version_finder/commit/b4bf5a9a036840aebc91c9ce389a9ff1ef293a1b))


## v3.3.3 (2024-11-26)

### Bug Fixes

* fix(gui): improve autocomplete ([`34d753a`](https://github.com/LevyMatan/version_finder/commit/34d753a65985b959bc8684a5e4d66161c67b4537))


## v3.3.2 (2024-11-26)

### Bug Fixes

* fix(versioning): Update the release workflow ([`9d00b06`](https://github.com/LevyMatan/version_finder/commit/9d00b0660e8d3c9ec8c0ec5d04296686579e4cdd))

### Unknown

* Merge pull request #52 from LevyMatan/version-sync

fix(versioning): Update the release workflow ([`2f6c77a`](https://github.com/LevyMatan/version_finder/commit/2f6c77a5774b9b4cd9e0d96f16c93137cc9a051a))


## v3.3.1 (2024-11-26)

### Bug Fixes

* fix(versioning): fix the version reported

- sync the way version is fetched
- allow semantic versioning action to update the files to update automatically ([`d318534`](https://github.com/LevyMatan/version_finder/commit/d318534ff056fb75f75475ae048f6b957e86024c))

### Unknown

* Merge pull request #51 from LevyMatan/version-sync

fix(versioning): fix the version reported ([`32994aa`](https://github.com/LevyMatan/version_finder/commit/32994aac27a4b49d7a94c322b160eadc5cb5d2ce))


## v3.3.0 (2024-11-26)

### Bug Fixes

* fix(ci): Change secert name, Github doesnt allow to use GITHUB_TOKEN ([`c19308c`](https://github.com/LevyMatan/version_finder/commit/c19308c0def782320e4ece4be221178f177fc4a2))

* fix(semantic-release): fetch entire git repo when cloning ([`68632d7`](https://github.com/LevyMatan/version_finder/commit/68632d7283b42ea58502ff36d8c0fec81247e223))

* fix(core): make the pattern for version case insensetive ([`6b03e92`](https://github.com/LevyMatan/version_finder/commit/6b03e924e66811850fb0ae005ff94fae20d10fd5))

* fix(core): submodule binary search fix --is-ancestor call by ignoring the exception on this case ([`c6d7e07`](https://github.com/LevyMatan/version_finder/commit/c6d7e072d7bcf1b9848205aa91bddeb0b7864f1e))

* fix(core): make search for version more robust ([`6b3b8cd`](https://github.com/LevyMatan/version_finder/commit/6b3b8cd5580ef0ef3a0e01d018be5742a21d5730))

* fix(ci): make the defualt branch to main ([`48bd0b3`](https://github.com/LevyMatan/version_finder/commit/48bd0b3cd9e7905ec81606c668464f49c1747053))

* fix(misc): ignore virtual env folder ([`b143512`](https://github.com/LevyMatan/version_finder/commit/b143512811e7539724e6c1d5807e1e9c16e93eb7))

* fix(test): change master to main ([`3374007`](https://github.com/LevyMatan/version_finder/commit/337400775303204ae976919db97978ede10681f7))

* fix(install): add missing dependency ([`12faedb`](https://github.com/LevyMatan/version_finder/commit/12faedb5e2c332980a7daab06e42f095ebc203ee))

* fix(ci): Used install-dev to get all dependencies ([`90553dc`](https://github.com/LevyMatan/version_finder/commit/90553dc8d9043da84d62811b9ef9fa8c53a36d32))

* fix(docs): Update readme setup instructions ([`dd1b4b1`](https://github.com/LevyMatan/version_finder/commit/dd1b4b14a6f70a2b466abbba255a10beb0d45d13))

### Chores

* chore(version): Update core version to 1.1.0 ([`de913a0`](https://github.com/LevyMatan/version_finder/commit/de913a07eaeec835f2f3a11228c01cc213919814))

### Features

* feat(ci): Allow manual trigger of release and coverage ([`7b6d9ce`](https://github.com/LevyMatan/version_finder/commit/7b6d9cef15b210217a209bcafcef7296a724d273))

* feat(cli): Add unit tests ([`7a9d1ba`](https://github.com/LevyMatan/version_finder/commit/7a9d1ba2c2fa1d067d47ce93e053b3793e48f924))

* feat(misc): Add cli debuger configuration to vscode ([`34792a5`](https://github.com/LevyMatan/version_finder/commit/34792a5df5da30708e8ff6e6015d4bea5dec25ea))

* feat(test): Add test for __extract_version_from_message ([`1e5df57`](https://github.com/LevyMatan/version_finder/commit/1e5df57b7acf7ade8da9a2b9e14c07ddcd9580ef))

* feat(ci): Upgrade setup-python to version 5 ([`eddf625`](https://github.com/LevyMatan/version_finder/commit/eddf625029f5c6ef129224c2d75b1b20fc5b5deb))

* feat(ci): run CI ([`876f85d`](https://github.com/LevyMatan/version_finder/commit/876f85de5632f6a3b1d34d7fc948d0c703b3615d))

* feat(GUI): Create a modern simple GUI to interact with VersionFinder

- Add autocomplete for branch and submodule
- Add error logging for user
- Initialize a versionFinder instance on chosen repo path ([`1aeb2d8`](https://github.com/LevyMatan/version_finder/commit/1aeb2d8a1660929789ea6b04319560d98c5eaf2b))

* feat(core): Add get_version_of_commit ([`6bf4838`](https://github.com/LevyMatan/version_finder/commit/6bf4838bb8dddde8fa4a97b574c010e7316a3344))

* feat(automation): Add Makefile with basic commands

The commands are: test, coverage, format, lint, clean ([`e005f08`](https://github.com/LevyMatan/version_finder/commit/e005f085fc828bdd3d87976fb24deebd711e4e64))

* feat(test): Add unit testing ([`ebb1d1d`](https://github.com/LevyMatan/version_finder/commit/ebb1d1d4e3dfe9e21bd857b138ad5c22b90abd65))

* feat(create test repo): create a complex repo with many commits ([`eb6aee9`](https://github.com/LevyMatan/version_finder/commit/eb6aee94b71dd5d6941a0f05bb6dfeba0e4fde15))

* feat: Add commit search functionality and improve repository handling

- Add new find_commits_by_text functionality in main
- Improve remote repository handling with __has_remote check
- Only fetch from remote when repository has remotes configured
- Fix string formatting to use %s style in logging statements
- Add type hint for Dict, Any in imports ([`90bdb3a`](https://github.com/LevyMatan/version_finder/commit/90bdb3a6bd404f2769d7269a33e1521136393483))

### Unknown

* Merge pull request #50 from LevyMatan/ci-feat

fix(ci): Change secert name, Github doesnt allow to use GITHUB_TOKEN ([`cfe57a5`](https://github.com/LevyMatan/version_finder/commit/cfe57a50ff8192165698f53ad573829934200d81))

* Merge pull request #49 from LevyMatan/ci-feat

Ci feat ([`2955e1e`](https://github.com/LevyMatan/version_finder/commit/2955e1e6f2347a71b7ce80cd81c1bd05c017b342))

* Merge pull request #48 from LevyMatan:ci-feat

feat(ci) Add semantic versioning ([`da6b252`](https://github.com/LevyMatan/version_finder/commit/da6b252a6f51451b3a70a2e9a86312d71f45e199))

* feat(ci) Add semantic versioning ([`c1c7bec`](https://github.com/LevyMatan/version_finder/commit/c1c7becbe9fc55a8c6e629fe19677399d4cf1d4c))

* Merge pull request #47 from LevyMatan/cli-test

feat(cli): Add unit tests ([`61e7da9`](https://github.com/LevyMatan/version_finder/commit/61e7da90d6aab838068b600ed675c77f7d10a594))

* Merge pull request #46 from LevyMatan/misc-debug

feat(misc): Add cli debugger configuration to vscode ([`92de02f`](https://github.com/LevyMatan/version_finder/commit/92de02fc7e13a33670286f680bd68d9d3ccf9ffa))

* Merge pull request #45 from LevyMatan/cli-improve

feat(cli) Major improvement to CLI interface ([`e2ed32a`](https://github.com/LevyMatan/version_finder/commit/e2ed32ae3d22538e493a90983607f858bbac455f))

* feat(cli) Major improvment to CLI interface

Also includes bug fix in core with the next version ([`e2f954b`](https://github.com/LevyMatan/version_finder/commit/e2f954b307066fde726657acbfc91608b956bece))

* Merge pull request #44 from LevyMatan/doc-readme

doc(readme): improve usage section and code structure ([`077f638`](https://github.com/LevyMatan/version_finder/commit/077f638441c9680cda96cea845fc59726a6fa057))

* doc(readme): improve usage section and code structure ([`6ccb0bf`](https://github.com/LevyMatan/version_finder/commit/6ccb0bfeb0e0cea1b47caaa9c0f87e3536d0e3fa))

* Merge pull request #43 from LevyMatan/search_fix

fix(core): make the pattern for version case insensetive ([`1697eb8`](https://github.com/LevyMatan/version_finder/commit/1697eb87b063aec85ed31b3b3025594f5b3d3c8a))

* Merge pull request #42 from LevyMatan/core-fixes

Core fixes ([`fa9d655`](https://github.com/LevyMatan/version_finder/commit/fa9d655ffd1dddea143730f671b1c1814e1e200c))

* refactor(): rename several functions in VersionFinder ([`6a16d7a`](https://github.com/LevyMatan/version_finder/commit/6a16d7a62e64e539301e0421bdc98539578824b8))

* Merge pull request #41 from LevyMatan/core-fixes

fix(core): submodule binary search fix --is-ancestor call by ignoring… ([`c04b981`](https://github.com/LevyMatan/version_finder/commit/c04b98180ddadbf1bb135662ea29a1655a4a2230))

* Merge pull request #40 from LevyMatan/core-fixes

fix(core): make search for version more robust ([`2d1e9db`](https://github.com/LevyMatan/version_finder/commit/2d1e9db266b381f0901c2d81e12797fe8c7415f5))

* Merge pull request #39 from LevyMatan/ci-changes

fix(ci): make the defualt branch to main ([`551fb1a`](https://github.com/LevyMatan/version_finder/commit/551fb1ab77733c79ee7077f0b8c353454410297f))

* Merge pull request #38 from LevyMatan/misc-fixes

fix(misc): ignore virtual env folder ([`d2f8d53`](https://github.com/LevyMatan/version_finder/commit/d2f8d531126f5cca37e19ed19b706192627a200e))

* Merge pull request #37 from LevyMatan/test-fixes

fix(test): change master to main ([`30bb2f5`](https://github.com/LevyMatan/version_finder/commit/30bb2f5b35ea62171741d3555ba7c95f37be0a0b))

* Merge pull request #36 from LevyMatan/setup-fixes

fix(install): add missing dependency ([`99900ad`](https://github.com/LevyMatan/version_finder/commit/99900ad3ce54d9dfa58e7d5a98eda8f0da195fdf))

* Merge pull request #35 from LevyMatan/ci-changes

feat(ci): Upgrade setup-python to version 5 ([`eb679f3`](https://github.com/LevyMatan/version_finder/commit/eb679f3b8a704bc02a2f9343d430498e153c304a))

* Merge pull request #34 from LevyMatan/feature/python_module

fix(ci): Used install-dev to get all dependencies ([`71bb935`](https://github.com/LevyMatan/version_finder/commit/71bb935fc2f6642db9b77d49ffe4bd5b24ab9cce))

* Merge pull request #33 from LevyMatan/feature/python_module

Feature/python module ([`6e01fb9`](https://github.com/LevyMatan/version_finder/commit/6e01fb9f93a7294bbea149f2c0b2fcb795324f36))

* feat(common) make arg parser as common for cli core and gui ([`60e6998`](https://github.com/LevyMatan/version_finder/commit/60e699864489e3cbbf0db5dce35bd68040217140))

* Split to core cli and gui ([`759c535`](https://github.com/LevyMatan/version_finder/commit/759c5350da4a7b0743ebc71016f37b59f3af7012))

* pep8 ([`1d89ba9`](https://github.com/LevyMatan/version_finder/commit/1d89ba93360659cd904a4244324e659b26b3a6e7))

* Clean pylint warnings ([`ca4cfbe`](https://github.com/LevyMatan/version_finder/commit/ca4cfbe725d0b3c52f9868558085fe607ec545a5))

* validate repo path ([`db6b5ee`](https://github.com/LevyMatan/version_finder/commit/db6b5eeb20c24f13d2d69f273b9e2706f07292aa))

* remove parallel code ([`d49674a`](https://github.com/LevyMatan/version_finder/commit/d49674a78dec01f7677d381ffa7b1031d6680f7c))

* Add git config test ([`f6bacb6`](https://github.com/LevyMatan/version_finder/commit/f6bacb611ab040e72a7dc4c40a166612c894ab01))

* Remove unused methods ([`03b4139`](https://github.com/LevyMatan/version_finder/commit/03b4139294c372177d30b5c1262e3040e91fccdf))

* type hiniting ([`a19288e`](https://github.com/LevyMatan/version_finder/commit/a19288e957408f4cb4a18d5aff456eb88040d918))

* pep8 ([`9703c33`](https://github.com/LevyMatan/version_finder/commit/9703c336d709d0999324fcf6779331dfaf60e914))

* bug(parallel submodule init): remove parallel execution ([`47f50a2`](https://github.com/LevyMatan/version_finder/commit/47f50a23a9c4b4a3d4642bbbc6ab39be28cd3e2b))

* version and submodule methods ([`0b84660`](https://github.com/LevyMatan/version_finder/commit/0b84660ea6c7ad75bfd87e44fee0be66cc50e586))

* feat(core) find superproject commit that contains submodule commit ([`dfa4df3`](https://github.com/LevyMatan/version_finder/commit/dfa4df3072fdb1c982a854b317ab89528f5ad65e))

* Add docstring to __init__.py ([`774a9e7`](https://github.com/LevyMatan/version_finder/commit/774a9e787e78709020e1510ae80bf76ea005509a))

* Improve finding surrounding commits ([`890a995`](https://github.com/LevyMatan/version_finder/commit/890a9950bd228040763fee7404c1a2ddcd434c16))

* get surrounding commits ([`54ea0dc`](https://github.com/LevyMatan/version_finder/commit/54ea0dc728fc619e7e5528d91c52055249f90909))

* autopep8 ([`ab9b101`](https://github.com/LevyMatan/version_finder/commit/ab9b101bc82c0e834f8b6323721c6d7b8a855c24))

* pep8 ([`42a4c46`](https://github.com/LevyMatan/version_finder/commit/42a4c46e8f71cb66f5f8f0e756ac87b423a0178d))

* Add flake8 and autopep8 ([`abb66cd`](https://github.com/LevyMatan/version_finder/commit/abb66cd5a2ac1319f689c2580542f786c2e8ed1d))

* Fix setup ([`9300601`](https://github.com/LevyMatan/version_finder/commit/930060158e0ba3b100f7f9762fcd0fc00e708e15))

* Reorganize project ([`44ff968`](https://github.com/LevyMatan/version_finder/commit/44ff968d3b83d1e5cbf68aee9b4b4e7e7bcebaf0))

* Update git ignore ([`d55ef09`](https://github.com/LevyMatan/version_finder/commit/d55ef0923ce6ef8db54a47d347d460bd83c98a3c))

* Remove requierments.txt ([`79367be`](https://github.com/LevyMatan/version_finder/commit/79367be32383bf0a28ea3dafed83c5d205dc5e80))

* Add pytest ([`01eacb6`](https://github.com/LevyMatan/version_finder/commit/01eacb6057400c977f8f0ad26b48a0e80af1727b))

* Ignore vscode json ([`30b57b7`](https://github.com/LevyMatan/version_finder/commit/30b57b7986fb2516aef4031f7aeb898df14337a8))

* Improve efficiency ([`433f4c7`](https://github.com/LevyMatan/version_finder/commit/433f4c71fdf75763dcb4d486bca0cfef471852b3))

* Update README.md

Update installation instructions to add contribution ([`6f7f1e0`](https://github.com/LevyMatan/version_finder/commit/6f7f1e0747c8d18fe02ba15510353b499f798e54))

* Update setup.py

Add dev requirements in the setup ([`8366fdb`](https://github.com/LevyMatan/version_finder/commit/8366fdb3f9628bce5e5ef8d22548fd5470ac4085))

* Add CLI to find a commit ([`2c9d25a`](https://github.com/LevyMatan/version_finder/commit/2c9d25adac901de7ee50832211ee2693ba677d2f))

* [FEATURE] time the preformance of branch loading ([`36ebb30`](https://github.com/LevyMatan/version_finder/commit/36ebb306246ec1d0a9d51cdd33c60b1112a7fdd2))

* [BUG] git fetch before reading submodule and branches ([`7ff5f74`](https://github.com/LevyMatan/version_finder/commit/7ff5f74dec3fea476014026c4197b59c4da8cb6e))

* [FEATURE] Create a test repo to validate version finder code ([`77bfb7a`](https://github.com/LevyMatan/version_finder/commit/77bfb7addda32bbff739a2ced381f635287f51e9))

* [VERSION] 0.1.0 ([`82b4939`](https://github.com/LevyMatan/version_finder/commit/82b4939f7e5a4c6b9e05662c1fe47bd0e56b06e6))

* [BUG] Remove time from logger string ([`f480404`](https://github.com/LevyMatan/version_finder/commit/f480404fbf7ae9fda4d99add3c8a8e3b448524f1))

* [BUG] Sort branches ([`a11f6ac`](https://github.com/LevyMatan/version_finder/commit/a11f6acbd0314508fc9a36fcf11edf197bb69708))

* [BUG] Sort branches ([`450b2f7`](https://github.com/LevyMatan/version_finder/commit/450b2f721e758081be915dcf633fba2f91f08d6e))

* [BUG] exclude branch name with * ([`7e38103`](https://github.com/LevyMatan/version_finder/commit/7e38103d91e14fa809d9c2f0cb9a14a7568b4934))

* [BUG] remove duplicates from branch list ([`3ededcf`](https://github.com/LevyMatan/version_finder/commit/3ededcfad97948425b8bc8eaa482b76f1073f9c6))

* [BUG] Fetch all branches, both local and remote ([`7858751`](https://github.com/LevyMatan/version_finder/commit/7858751372a113239724ca564acc1b83b69b2df8))

* [BUG] fetch branches names to clean only origin prefix ([`51d721e`](https://github.com/LevyMatan/version_finder/commit/51d721ebfaa2cfcc1deb076c17d6fe32a4626d91))

* [BUG] add debug to print branch names ([`4fa7721`](https://github.com/LevyMatan/version_finder/commit/4fa7721e61b4616af475f8fdaa16e89a13e250d4))

* [DOC] Rewrite README file ([`ade4bc2`](https://github.com/LevyMatan/version_finder/commit/ade4bc232a040d040361be0b498964e665270bc1))

* [BUG] Remove redundent file for python module ([`3e3fea5`](https://github.com/LevyMatan/version_finder/commit/3e3fea5710618a21448771e83a6d1bbfd9767e96))

* Add files via upload ([`85af8bc`](https://github.com/LevyMatan/version_finder/commit/85af8bcb8b84edddb70040ba3249bc31a85c069f))


## v3.2.1 (2024-06-30)

### Bug Fixes

* fix(ci): When a single platform build fails, continue with others. ([`49012d5`](https://github.com/LevyMatan/version_finder/commit/49012d54c003942abdb9c18a90db4d74bc0fd601))

* fix: linux packaging command ([`d75c076`](https://github.com/LevyMatan/version_finder/commit/d75c0764d56a5ef2570d442ef08e43dd4a4db4d8))

### Documentation

* docs: Update installation instructions with download link

The installation instructions in the README.md file have been updated to include a direct download link for the latest version of the app from the Releases page. Additionally, a note has been added to specify that the app is only available for macOS and Linux platforms. ([`bde1015`](https://github.com/LevyMatan/version_finder/commit/bde1015b4b9a24df4a3bfc8eafec11d1aea9e04e))

### Unknown

* Version: 3.2.1

## [3.2.1](https://github.com/LevyMatan/version_finder/compare/v3.2.0...v3.2.1) (2024-06-30)

### Bug Fixes

* **ci:** When a single platform build fails, continue with others. ([49012d5](https://github.com/LevyMatan/version_finder/commit/49012d54c003942abdb9c18a90db4d74bc0fd601))
* linux packaging command ([d75c076](https://github.com/LevyMatan/version_finder/commit/d75c0764d56a5ef2570d442ef08e43dd4a4db4d8)) ([`03d3faa`](https://github.com/LevyMatan/version_finder/commit/03d3faab589ed9b8020bf7742fb524487b9e8ddc))

* Merge pull request #32 from LevyMatan/docs

fix: linux build, CI fail-fast setting ([`dbbb41a`](https://github.com/LevyMatan/version_finder/commit/dbbb41aeac204cbeb429bf19c66f287a7899e1bd))


## v3.2.0 (2024-06-30)

### Chores

* chore: Add logo and icons assests ([`aa6901e`](https://github.com/LevyMatan/version_finder/commit/aa6901e2c927451fe31d9b6abcd6df9e5729c9c0))

### Features

* feat: Update icons for macOS and Linux platforms ([`f899d0b`](https://github.com/LevyMatan/version_finder/commit/f899d0b527e64296199270c66a852374062c0a66))

### Refactoring

* refactor: Apply format to index.html ([`5767453`](https://github.com/LevyMatan/version_finder/commit/576745348f8132a294b74eb8e1c893d69ca9fd01))

* refactor: Update .gitignore to ignore .DS_Store file

The .gitignore file has been updated to ignore the .DS_Store file. This file is automatically created by macOS and can be safely ignored in the repository. ([`99dc227`](https://github.com/LevyMatan/version_finder/commit/99dc2278144872324d59f3876dbe6571ba9dbd55))

* refactor: Update icon paths in package.json and index.html

The icon paths in the package.json and index.html files have been updated to use the new version-finder-icon.icns file. This ensures that the correct icon is displayed for the application on both macOS and Linux platforms. ([`9711963`](https://github.com/LevyMatan/version_finder/commit/9711963fd6f29e572bff479e50fd4aaf9e3f4304))

### Unknown

* Version: 3.2.0

# [3.2.0](https://github.com/LevyMatan/version_finder/compare/v3.1.0...v3.2.0) (2024-06-30)

### Features

* Update icons for macOS and Linux platforms ([f899d0b](https://github.com/LevyMatan/version_finder/commit/f899d0b527e64296199270c66a852374062c0a66)) ([`8d7c523`](https://github.com/LevyMatan/version_finder/commit/8d7c5230363cd9552837070639d203d5f77b087a))

* Merge pull request #31 from LevyMatan/docs

feat: Update icons and logo ([`b4b9131`](https://github.com/LevyMatan/version_finder/commit/b4b9131c4ce5314a44a5f569d3b373e03f3ca07f))


## v3.1.0 (2024-06-28)

### Bug Fixes

* fix: Remove unused mainWindow.versionFinder property ([`a1c7404`](https://github.com/LevyMatan/version_finder/commit/a1c74049e0b09d1a106cf53f849fb0c6dde98d0d))

### Chores

* chore: Add unnecessary console.log statement in getLogs test ([`d8c54b1`](https://github.com/LevyMatan/version_finder/commit/d8c54b1d350ef10c860092c4954b4eba0cd8bcf3))

* chore: Refactor unit-tests getSubmodules and getBranches methods ([`59ec519`](https://github.com/LevyMatan/version_finder/commit/59ec519ca17c7701f7d81addafb911884bdf0f27))

* chore: Refactor VersionFinder class to use async/await for restoring repository snapshot ([`b689519`](https://github.com/LevyMatan/version_finder/commit/b689519fd47f20cf2050036ed2b8bef74feb1159))

* chore: Add require-await rule for linter ([`bb84824`](https://github.com/LevyMatan/version_finder/commit/bb84824981dd549c85d2c8132bcfa7816813f217))

* chore: Refactor VersionFinder class and update getLogs method

Remove unnecessary parameter from getLogs method and refactor the VersionFinder class to improve code organization and readability. ([`93541be`](https://github.com/LevyMatan/version_finder/commit/93541bebc1709416fa89b150655be4d81c9f8daa))

* chore: Update getLogs method to remove unnecessary parameter ([`c41af1c`](https://github.com/LevyMatan/version_finder/commit/c41af1cefb922e09eb04f00703d3449ef197a6b7))

* chore: use async/await for restoring repository snapshot ([`5cf1d90`](https://github.com/LevyMatan/version_finder/commit/5cf1d9061f5a98b7aa812310552f8a3be378e306))

* chore: Refactor VersionFinder class to improve code organization and readability ([`54e2b22`](https://github.com/LevyMatan/version_finder/commit/54e2b22a6661541af301a2563255ec1a87051622))

* chore: Update IPC event name for saving repository state, add comments, adjust saveRepoState also for clean repos ([`6e4c22e`](https://github.com/LevyMatan/version_finder/commit/6e4c22eebd6ce8c2438ea826850910275f28b08f))

### Features

* feat(core): Store repo state, if any checkout occures, the state is restored

29-branch-change-not-restored ([`3f41f6b`](https://github.com/LevyMatan/version_finder/commit/3f41f6bb6887bbb97d12c2e98920407828412d09))

### Refactoring

* refactor: Remove unnecessary assignment of false to hasChanges property in VersionFinder class ([`095c02a`](https://github.com/LevyMatan/version_finder/commit/095c02a3aed5862db21230e7876f2ea469ebc5fc))

* refactor: Update VersionFinder class to use async/await for checking repository dirtiness during initialization ([`7ca58d6`](https://github.com/LevyMatan/version_finder/commit/7ca58d6b6bd0ed9500711a061e9870d6c49a700a))

* refactor: Improve logger.js by handling errors when parsing additional data

The logger.js file has been updated to handle errors that may occur when parsing additional data. This ensures that any errors encountered during the formatting of additional arguments (splat) are caught and logged. This change improves the robustness of the logger functionality. ([`5ebae6a`](https://github.com/LevyMatan/version_finder/commit/5ebae6a3308a7c95df8f2ca68a451c7d76ac3aae))

* refactor: files format ([`aab520a`](https://github.com/LevyMatan/version_finder/commit/aab520a742592a2c4cecff598d8fb3001ffa25c2))

* refactor: Update VersionFinder class to check repository dirtiness during initialization

The `hasChanges` property in the VersionFinder class is now set by calling the `isRepoDirty` method during initialization. This ensures that the `hasChanges` property accurately reflects the repository's dirtiness. The unnecessary assignment of `false` to `hasChanges` has been removed. ([`6825575`](https://github.com/LevyMatan/version_finder/commit/6825575639f259d0862ff9d18421b352dcc2d451))

### Unknown

* Version: 3.1.0

# [3.1.0](https://github.com/LevyMatan/version_finder/compare/v3.0.0...v3.1.0) (2024-06-28)

### Bug Fixes

* Remove unused mainWindow.versionFinder property ([a1c7404](https://github.com/LevyMatan/version_finder/commit/a1c74049e0b09d1a106cf53f849fb0c6dde98d0d))

### Features

* **core:** Store repo state, if any checkout occures, the state is restored ([3f41f6b](https://github.com/LevyMatan/version_finder/commit/3f41f6bb6887bbb97d12c2e98920407828412d09)) ([`1848fd1`](https://github.com/LevyMatan/version_finder/commit/1848fd1e80d2adb26fdcf2bf37764b3b9a9c2673))


## v3.0.0 (2024-06-27)

### Breaking

* fix(submodules list): return empty list when no submodules

BREAKING CHANGE: Instead returning a list with the value: "No submodules in Repo"
return an empty list ([`16e7675`](https://github.com/LevyMatan/version_finder/commit/16e7675e11705f0161d3b3847b6cce29f764428a))

* feat(core): Add snapshot mechanisim for dirty repos

BREAKING CHANGE: The change introduced will stash any changes and save the current commit hash. After it finishes the operations, it restores all. ([`c015bc8`](https://github.com/LevyMatan/version_finder/commit/c015bc8764b61e36bd7ba89c48d76e2ec22a4350))

### Bug Fixes

* fix(submodule-list): handle empty list in renderer ([`4bfb415`](https://github.com/LevyMatan/version_finder/commit/4bfb415717d86347eefd68e5ef6e1bb21d079727))

* fix(test): rewrite the file ([`acbbd9b`](https://github.com/LevyMatan/version_finder/commit/acbbd9bae902a6862998f436852c89639f9ad7eb))

* fix(test): reorder changing files to git init ([`ab00b5d`](https://github.com/LevyMatan/version_finder/commit/ab00b5dd02af05da0864bc674fbcd8f28fecd6e7))

* fix(test): modify an existing file instead of creating a new file ([`4244c37`](https://github.com/LevyMatan/version_finder/commit/4244c3760a22df27b89633fc95408db25c75f55a))

* fix: Add test.txt file with "Hello World!" content ([`a78c10a`](https://github.com/LevyMatan/version_finder/commit/a78c10ae4a1baacdd73698dcc1791aba458e9e73))

### Chores

* chore(unit-test): Add saveRepoSnapshot and restoreRepoSnapshot methods to VersionFinder tests ([`01220b8`](https://github.com/LevyMatan/version_finder/commit/01220b8a148e8334bce0ac196bcc65baaf39ea42))

* chore(unit-test): Add isDirty tests ([`fe1da94`](https://github.com/LevyMatan/version_finder/commit/fe1da9428c8a12d449cb5a2e7602853703624c3c))

* chore: Refactor undoRepoSnapshot method in VersionFinder class ([`b0cad77`](https://github.com/LevyMatan/version_finder/commit/b0cad771953ff5f118d6405cb66b8cda256fef13))

* chore(test): Add cases handling for uncommitted changes in versionFinder tests ([`a9954d4`](https://github.com/LevyMatan/version_finder/commit/a9954d45aba4044f5b4e6add78c537277b8ed64a))

* chore: Remove new line added to test.txt file in afterEach hook ([`5de0b9b`](https://github.com/LevyMatan/version_finder/commit/5de0b9b5d76232b17f103acc2baa5334260402be))

* chore(unit-test): Update error message for unknown file in versionFinder test ([`441c102`](https://github.com/LevyMatan/version_finder/commit/441c1021d2a056fb1b8ba980147e09ffca186775))

* chore: Add isRepoDirty method to check if the repository has uncommitted changes ([`670e0c0`](https://github.com/LevyMatan/version_finder/commit/670e0c04eeff92cbe63e3807e0b9188a60ba6032))

* chore(test): Add testcase for a git repo with changes ([`a2c89d6`](https://github.com/LevyMatan/version_finder/commit/a2c89d603e0890aa2dad0e85834a7078a2c1d6f1))

### Unknown

* Version: 3.0.0

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
* **core:** The change introduced will stash any changes and save the current commit hash. After it finishes the operations, it restores all. ([`163c1f6`](https://github.com/LevyMatan/version_finder/commit/163c1f6ab245ebcc4a53fe9b822459c4ed3b7f69))

* Merge pull request #26 from LevyMatan:feature/save-repo-state

Add snapshot mechanism for dirty repos ([`fe891f3`](https://github.com/LevyMatan/version_finder/commit/fe891f358bd1ed18cb56857342566c64de4c3a96))

* Merge pull request #25 from LevyMatan/feature/ci-testing

Feature/ci testing ([`e61345a`](https://github.com/LevyMatan/version_finder/commit/e61345abb19ca2734dd2b39d248366434bd2635b))

* Merge branch 'main' into feature/ci-testing ([`7438fd4`](https://github.com/LevyMatan/version_finder/commit/7438fd4afd313fa4cb84233b58aaea3c36126cec))


## v2.1.5 (2024-06-26)

### Unknown

* Version: 2.1.5

## [2.1.5](https://github.com/LevyMatan/version_finder/compare/v2.1.4...v2.1.5) (2024-06-26)

### Bug Fixes

* **ci:** adjust the upload file path ([af1a721](https://github.com/LevyMatan/version_finder/commit/af1a721906f479f5d268a48d4d5c99a3623f0dc6)) ([`92db4f2`](https://github.com/LevyMatan/version_finder/commit/92db4f24cc33893549ed62f64576947897ce73cc))

* Merge pull request #24 from LevyMatan/feature/ci-testing

fix(ci): adjust the upload file path ([`4cb5858`](https://github.com/LevyMatan/version_finder/commit/4cb5858b8f074bbfdb5b816bd43101f1edbb099e))


## v2.1.4 (2024-06-26)

### Unknown

* Version: 2.1.4

## [2.1.4](https://github.com/LevyMatan/version_finder/compare/v2.1.3...v2.1.4) (2024-06-26)

### Bug Fixes

* **ci:** Split release-and-build workflow ([b08835d](https://github.com/LevyMatan/version_finder/commit/b08835d91a60dae5607f07fb0a570779f0974215)) ([`f7501e9`](https://github.com/LevyMatan/version_finder/commit/f7501e9c075c7d3c42e34c3608762f71aec339e3))

* Merge pull request #23 from LevyMatan/feature/ci-testing

fix(ci): Split release-and-build workflow ([`09d0f32`](https://github.com/LevyMatan/version_finder/commit/09d0f32ea9ac5423acdbe3534964d8a0aba4c1c1))


## v2.1.3 (2024-06-26)

### Unknown

* Version: 2.1.3

## [2.1.3](https://github.com/LevyMatan/version_finder/compare/v2.1.2...v2.1.3) (2024-06-26)

### Bug Fixes

* **ci:** Attach assets when a new Version commit is created ([fbd2c19](https://github.com/LevyMatan/version_finder/commit/fbd2c192ea5f031b51cf1c94230ebecc05f08abd)) ([`98e6616`](https://github.com/LevyMatan/version_finder/commit/98e66162daa968588613f4fa6acc1d9753239a38))

* Merge pull request #22 from LevyMatan/feature/ci-testing

fix(ci): Attach assets when a new Version commit is created ([`15cb126`](https://github.com/LevyMatan/version_finder/commit/15cb126da37851c2a7f005c0dd7c3509b34ce0c6))


## v2.1.2 (2024-06-26)

### Bug Fixes

* fix(ci): adjust the upload file path ([`af1a721`](https://github.com/LevyMatan/version_finder/commit/af1a721906f479f5d268a48d4d5c99a3623f0dc6))

* fix(ci): Split release-and-build workflow

Divide responsability of the work flow to two distingished.
The first, triggered by a push to master, will create a release using semantic-release.
The second, triggered by a published release, will attach assets to it ([`b08835d`](https://github.com/LevyMatan/version_finder/commit/b08835d91a60dae5607f07fb0a570779f0974215))

* fix(ci): Attach assets when a new Version commit is created ([`fbd2c19`](https://github.com/LevyMatan/version_finder/commit/fbd2c192ea5f031b51cf1c94230ebecc05f08abd))

* fix(ci): Disable the "Release" workflow ([`3f8a9b6`](https://github.com/LevyMatan/version_finder/commit/3f8a9b6cc5463c5796c2f11cde05bfe89138ca5f))

* fix(lint): Add jest and bootstrap globals ([`e513cae`](https://github.com/LevyMatan/version_finder/commit/e513cae7da7b5d2a678b0467af6c3b4a61d49854))

* fix: Update VersionFinder constructor to use dynamic branch for validation

The code changes update the VersionFinder constructor to use a dynamic branch for validation. Instead of hardcoding the branch name, the code now retrieves the branches from the repository and uses the first branch as the valid branch for initialization. This ensures that the VersionFinder object is properly initialized with a valid branch before any method is called that relies on its initialization state. ([`51835c2`](https://github.com/LevyMatan/version_finder/commit/51835c250598b9ec84895d1aac527288dc6f32bf))

### Chores

* chore(ci): add comments to workflow ([`253da1e`](https://github.com/LevyMatan/version_finder/commit/253da1e4490e3b55c79602aee1ac8c3c7b446442))

* chore(ci): remove unused workflow ([`e40f14c`](https://github.com/LevyMatan/version_finder/commit/e40f14c4f570f84fd78bb804d61c3c7c7d48eac8))

* chore: Update workflows to use ADMIN_PAT ([`ba049e8`](https://github.com/LevyMatan/version_finder/commit/ba049e88e6d16fad9522715de7268175743e92dd))

* chore: Update workflows for manual semantic release and unit testing

This commit updates the workflows for manual semantic release and unit testing. The previous workflow 'manual-semantic-release.yml' has been deleted, and a new workflow 'release-and-build.yml' has been added. Additionally, a new workflow 'unit-test.yml' has been added for running unit tests. These changes aim to improve the release process and ensure proper testing of the codebase. ([`816ba16`](https://github.com/LevyMatan/version_finder/commit/816ba1668f7159b3e45d3bb806cf093561968622))

* chore(testing): add jest as dependency ([`0c379c7`](https://github.com/LevyMatan/version_finder/commit/0c379c77f24f2a2d24e6671c66297f2050b956a5))

### Unknown

* Version: 2.1.2

## [2.1.2](https://github.com/LevyMatan/version_finder/compare/v2.1.1...v2.1.2) (2024-06-26)

### Bug Fixes

* **ci:** Disable the "Release" workflow ([3f8a9b6](https://github.com/LevyMatan/version_finder/commit/3f8a9b6cc5463c5796c2f11cde05bfe89138ca5f))
* **lint:** Add jest and bootstrap globals ([e513cae](https://github.com/LevyMatan/version_finder/commit/e513cae7da7b5d2a678b0467af6c3b4a61d49854))
* Update VersionFinder constructor to use dynamic branch for validation ([51835c2](https://github.com/LevyMatan/version_finder/commit/51835c250598b9ec84895d1aac527288dc6f32bf)) ([`3699527`](https://github.com/LevyMatan/version_finder/commit/36995277cb1d9218c05546672ea3ba05c7b24adf))

* Merge pull request #21 from LevyMatan/feature/ci-testing

Feature/ci-testing ([`bc04c78`](https://github.com/LevyMatan/version_finder/commit/bc04c789454859bcb4e02d792c2bad23e20a0f9d))

* Merge pull request #20 from LevyMatan/feature/ci-testing

Feature/ci testing ([`274e2a4`](https://github.com/LevyMatan/version_finder/commit/274e2a47967bb7592284b6b2801af864241ecafd))

* pref(ci): Run unit-tests only on relevant file changes ([`fec10f9`](https://github.com/LevyMatan/version_finder/commit/fec10f994b388529fb283cfb3dfe4920d8992e89))


## v2.1.1 (2024-06-25)

### Bug Fixes

* fix: Update .releaserc message format ([`3753ea5`](https://github.com/LevyMatan/version_finder/commit/3753ea5c56d966b1c3105f55f7616e04fb56efec))

### Chores

* chore(format): Apply prettier format for all files ([`6c5b713`](https://github.com/LevyMatan/version_finder/commit/6c5b7131859e7caf56b0ca6a3853ba54dd9f8d0b))

### Unknown

* Version: 2.1.1

## [2.1.1](https://github.com/LevyMatan/version_finder/compare/v2.1.0...v2.1.1) (2024-06-25)

### Bug Fixes

* Update .releaserc message format ([3753ea5](https://github.com/LevyMatan/version_finder/commit/3753ea5c56d966b1c3105f55f7616e04fb56efec)) ([`7758940`](https://github.com/LevyMatan/version_finder/commit/77589409e91fa4e0ed4c8302ac885517f4871f95))


## v2.1.0 (2024-06-25)

### Bug Fixes

* fix(main): import the version finder class ([`b1a443c`](https://github.com/LevyMatan/version_finder/commit/b1a443c874690e9d1a5afbe00653bf2ef3accb17))

### Chores

* chore(release): 2.1.0 [skip ci]

# [2.1.0](https://github.com/LevyMatan/version_finder/compare/v2.0.0...v2.1.0) (2024-06-25)

### Bug Fixes

* **main:** import the version finder class ([b1a443c](https://github.com/LevyMatan/version_finder/commit/b1a443c874690e9d1a5afbe00653bf2ef3accb17))

### Features

* Add check for uncommitted changes in VersionFinder initialization ([52a9f85](https://github.com/LevyMatan/version_finder/commit/52a9f85c01770aa3e331602dbaead4e3dadfa0c9))
* Add validation for search pattern in VersionFinder ([44e7438](https://github.com/LevyMatan/version_finder/commit/44e7438e5d8e202b3cc1e2b674fed2a2f9638ac5))
* **lint:** Add eslint ([e8b4920](https://github.com/LevyMatan/version_finder/commit/e8b4920b376d2b76042027b45c3ad30957743114))
* **version-finder:** Initialize VersionFinder in the constructor to set the 'isInitialized' flag to false. This ensures that the VersionFinder object is properly initialized before any method is called that relies on its initialization state. ([27f4750](https://github.com/LevyMatan/version_finder/commit/27f475036625f65ab33feddd4578a441feadea61)) ([`f770f0a`](https://github.com/LevyMatan/version_finder/commit/f770f0a3aed650ca1e1d256631801f0b27d65b7e))

* chore: Update .gitignore to ignore 'out/' directory

This commit updates the .gitignore file to ignore the 'out/' directory. This directory is typically used for output files generated during the build process and should not be tracked by version control. ([`0e0a0b4`](https://github.com/LevyMatan/version_finder/commit/0e0a0b41db799fa955cc200ed97c237af13f7f63))

* chore(code clean): remove duplicated comments and catch phrases ([`1269a69`](https://github.com/LevyMatan/version_finder/commit/1269a69a42bb796b9d0b848e90ebc370e00369f4))

* chore: Refactor error handling in renderer.js and main.js ([`af7ade5`](https://github.com/LevyMatan/version_finder/commit/af7ade59b9fd1b5f1793c44b80a18339597f3e71))

* chore: Update logger configurations dynamically ([`6ade626`](https://github.com/LevyMatan/version_finder/commit/6ade6262423a4ed6ff880dbb76219fc64cfc384e))

* chore(clean): Remove unused files and update package.json ([`99b496f`](https://github.com/LevyMatan/version_finder/commit/99b496f546e713d01456729b91f0d9c4e21aa91f))

### Features

* feat: Add validation for search pattern in VersionFinder

The code changes add validation for the search pattern in the VersionFinder class. It checks if the search pattern is a string and a valid regular expression. If the search pattern is not a string or not a valid regex, an error is thrown. This ensures that the search pattern is properly validated before performing any search operations. ([`44e7438`](https://github.com/LevyMatan/version_finder/commit/44e7438e5d8e202b3cc1e2b674fed2a2f9638ac5))

* feat: Add check for uncommitted changes in VersionFinder initialization

The commit adds a check for uncommitted changes in the VersionFinder initialization process. If there are any uncommitted changes, a warning is logged and the `hasChanges` flag is set to `true`. This ensures that the repository's state is taken into account when performing operations that rely on a clean repository. ([`52a9f85`](https://github.com/LevyMatan/version_finder/commit/52a9f85c01770aa3e331602dbaead4e3dadfa0c9))

* feat(version-finder): Initialize VersionFinder in the constructor to set the 'isInitialized' flag to false. This ensures that the VersionFinder object is properly initialized before any method is called that relies on its initialization state. ([`27f4750`](https://github.com/LevyMatan/version_finder/commit/27f475036625f65ab33feddd4578a441feadea61))

* feat(lint): Add eslint ([`e8b4920`](https://github.com/LevyMatan/version_finder/commit/e8b4920b376d2b76042027b45c3ad30957743114))

### Unknown

* Merge pull request #19 from LevyMatan:feature/save-repo-state

Code Improvments ([`d221c4c`](https://github.com/LevyMatan/version_finder/commit/d221c4c720d4702066945cadfd814def510643e0))

* Merge pull request #18 from LevyMatan:feature/add-logger

chore: Update logger configurations dynamically ([`971c5ed`](https://github.com/LevyMatan/version_finder/commit/971c5ed496b5a8de9d0cdc8a0a9c9cd9aa1767df))

* doc: Add documentation to main.js variables and functions ([`be401c6`](https://github.com/LevyMatan/version_finder/commit/be401c6229273ab25a22226d9dfa05c925f0b985))


## v2.0.0 (2024-06-22)

### Chores

* chore(release): 2.0.0 [skip ci]

# [2.0.0](https://github.com/LevyMatan/version_finder/compare/v1.1.0...v2.0.0) (2024-06-22)

* pref(ipc-comm)!: Improve preformance by changing the ipc communication. ([75609cb](https://github.com/LevyMatan/version_finder/commit/75609cbdecac9092eb052773ad8b95b75a88143f))

### BREAKING CHANGES

* The change in IPC (modyfing existing IPC) may break competability with imaginary third parties. ([`9cd808e`](https://github.com/LevyMatan/version_finder/commit/9cd808e2464f25a820db5433d82ff352db6cc48f))

### Unknown

* pref(ipc-comm)!: Improve preformance by changing the ipc communication.
BREAKING CHANGE: The change in IPC (modyfing existing IPC) may break competability with imaginary third parties. ([`75609cb`](https://github.com/LevyMatan/version_finder/commit/75609cbdecac9092eb052773ad8b95b75a88143f))


## v1.1.0 (2024-06-22)

### Bug Fixes

* fix(logging): remove the log file from repo ([`0c3aa76`](https://github.com/LevyMatan/version_finder/commit/0c3aa766f49747e5fa3bfda74b1b6333d626019a))

### Chores

* chore(release): 1.1.0 [skip ci]

# [1.1.0](https://github.com/LevyMatan/version_finder/compare/v1.0.0...v1.1.0) (2024-06-22)

### Bug Fixes

* **logging:** remove the log file from repo ([0c3aa76](https://github.com/LevyMatan/version_finder/commit/0c3aa766f49747e5fa3bfda74b1b6333d626019a))

### Features

* **logging:** Add logger - with control through settings ([11988e0](https://github.com/LevyMatan/version_finder/commit/11988e0f2be18c82d2c1c90d38a26bd07111b7fa))
* **logging:** Add open log file button at settings page ([3771f54](https://github.com/LevyMatan/version_finder/commit/3771f54a09f08c5f62423500170d216113106ff2)) ([`f1963f0`](https://github.com/LevyMatan/version_finder/commit/f1963f008a9152ec78743ccd476090f739c078f8))

* chore(logs): Add Winston log to package ([`267261a`](https://github.com/LevyMatan/version_finder/commit/267261ac13b92887b6720757ddf8a5b0e5135c43))

* chore(ci): Add debug for semantic-release action ([`c0911c8`](https://github.com/LevyMatan/version_finder/commit/c0911c8de937753f70929b636148e5ae147fc959))

### Features

* feat(logging): Add open log file button at settings page ([`3771f54`](https://github.com/LevyMatan/version_finder/commit/3771f54a09f08c5f62423500170d216113106ff2))

* feat(logging): Add logger - with control through settings ([`11988e0`](https://github.com/LevyMatan/version_finder/commit/11988e0f2be18c82d2c1c90d38a26bd07111b7fa))

### Unknown

* pref(git): skip repo-init when DOM is loaded.
BREAKING_CHANGE: Instead of calling the repo-init when the DOM is loaded, give the user the option to set the repo path before that. If the path does not change, once clicked on the branch text box, the init will be sent to fetch the list. ([`8a2c184`](https://github.com/LevyMatan/version_finder/commit/8a2c18450a3d44d593ac979e191b6adee73b50c2))

* Merge pull request #17 from LevyMatan:feature/add-logger

Feature/add-logger ([`117e167`](https://github.com/LevyMatan/version_finder/commit/117e1671369fb1e918a18aa72c1d384dccabcaef))


## v1.0.0 (2024-06-21)

### Bug Fixes

* fix(ci): pass GH_TOKEN instead of GITHUB_TOKEN ([`5a90496`](https://github.com/LevyMatan/version_finder/commit/5a904960693a022c064f3c9e2c8496d17854bd7d))

* fix(ci): Add github token to semantic-release ([`bcce626`](https://github.com/LevyMatan/version_finder/commit/bcce62639fc2ed33b0f7c56e9a04318bb09e1bdb))

* fix(ci): npm version on github runner ([`8c5feb3`](https://github.com/LevyMatan/version_finder/commit/8c5feb301c0c468928a2d20f2972725632bbcec0))

* fix: Clear branch and submodule input fields in resetForm function ([`326e24d`](https://github.com/LevyMatan/version_finder/commit/326e24d60aef96309ac7f6dfb40add56248a7b51))

* fix: adjust the file path ([`cf1feb0`](https://github.com/LevyMatan/version_finder/commit/cf1feb05297d18bf1e02f1445575904a891568a0))

* fix: submodules names ([`c5bdffd`](https://github.com/LevyMatan/version_finder/commit/c5bdffd8c1e534a4d0c3da068aa3e42653cedd5f))

### Chores

* chore(release): 1.0.0 [skip ci]

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
* **versioning:** Add semantic release ([137fd5a](https://github.com/LevyMatan/version_finder/commit/137fd5ab3200123b71e203f05ab76d191a904722)) ([`a2e7ab1`](https://github.com/LevyMatan/version_finder/commit/a2e7ab121825e43579811b6e302ae00411ec8b5b))

* chore(ci): try to change the access key ([`46e4ae2`](https://github.com/LevyMatan/version_finder/commit/46e4ae2b3b0c2f6fd6cd80c2f5323ef83378b683))

* chore(ci): update to version 4 ([`53dc32d`](https://github.com/LevyMatan/version_finder/commit/53dc32dccc79902f1a193383e6697b0dd4b30032))

* chore(ci): Try to use an action for semantic-release ([`f2518ea`](https://github.com/LevyMatan/version_finder/commit/f2518eaaca3d18f6c69f87e719f1b005e94de292))

* chore: Update style.css and main.js for centered heading and add top margin/padding to h1 ([`eda013d`](https://github.com/LevyMatan/version_finder/commit/eda013d6104afebfc621e103123b1d40a2cc08ef))

* chore: Update settings.html to include additional information about version search pattern customization ([`3fefce2`](https://github.com/LevyMatan/version_finder/commit/3fefce2e165890536f750824b438913c8b42b5cf))

* chore: Add ability to add new search patterns in settings ([`216200d`](https://github.com/LevyMatan/version_finder/commit/216200d7918884d261e7d17fee6334056956a1dd))

* chore: Refactor search pattern options creation in settings.js ([`894bb4b`](https://github.com/LevyMatan/version_finder/commit/894bb4bbe19d7881c90fcafd2da8c7c0018f97ec))

* chore: Update settings.html to include Bootstrap bundle and settings.js ([`8fedaf2`](https://github.com/LevyMatan/version_finder/commit/8fedaf27864ef8d2dd7113564da5fe92a5df99c8))

* chore: Refactor settings creation in main.js ([`58ef0f3`](https://github.com/LevyMatan/version_finder/commit/58ef0f3a7270171af68908a6eb1dbd51d2f9a66d))

* chore: Remove unused imports and update VersionFinder initialization ([`0873cef`](https://github.com/LevyMatan/version_finder/commit/0873cef8db316e3208019e85ee114d824cf00964))

* chore: Remove commented out code for launching demo modal ([`ef9db0a`](https://github.com/LevyMatan/version_finder/commit/ef9db0aee0f9aa6ede5ddb332eb712632149e2f4))

* chore: Add form validation and error handling to version finder form ([`197b4d9`](https://github.com/LevyMatan/version_finder/commit/197b4d9e1a343e8a39bfe57b2e9ee0fb96bc0f73))

* chore: Update build scripts to use correct icon paths ([`ee6ea65`](https://github.com/LevyMatan/version_finder/commit/ee6ea65a5d7e8b72e463fc6b4f63d845e974dab8))

* chore: clean code and comments ([`bf9e574`](https://github.com/LevyMatan/version_finder/commit/bf9e574df8df8d64953fb6a2bcd6fa0bc0071874))

* chore: add spinner modal for processing message ([`47e4737`](https://github.com/LevyMatan/version_finder/commit/47e47371b148978538eb475852ba80b432d8850c))

* chore: Update firstCommitMessage and versionCommitMessage display in renderer.js ([`8bdac0e`](https://github.com/LevyMatan/version_finder/commit/8bdac0e437bc2271906a122a31c0ad492e7187cf))

* chore: Update index.html to fix version display issue ([`d6f6d97`](https://github.com/LevyMatan/version_finder/commit/d6f6d97d1e354036bd686897b8d71e0b0bdca4e9))

* chore: Refactor searchVersion function to accept form object directly ([`cc0a93a`](https://github.com/LevyMatan/version_finder/commit/cc0a93a2fb01531d166271e6c11afd26a517667e))

* chore: Handle error fetching first commit SHA in version_finder.js ([`41dd959`](https://github.com/LevyMatan/version_finder/commit/41dd959dee1d195f7a84a9293a48dcc028378621))

* chore: Add extra top space to primary button ([`b9690b5`](https://github.com/LevyMatan/version_finder/commit/b9690b5bb6b4bf24c7438579eaf4dc42897f7b5e))

* chore: Update button style and position in index.html ([`c4cbfe0`](https://github.com/LevyMatan/version_finder/commit/c4cbfe0fb173e7fe4d6ee55997d08c92d57d0739))

* chore: use modal to display results ([`ff18aeb`](https://github.com/LevyMatan/version_finder/commit/ff18aeb4fbb3d35e75df1f9dd8b0caa203e3f48e))

* chore: split publish jobs ([`304685b`](https://github.com/LevyMatan/version_finder/commit/304685bfe3e6db65c1087a1a38c8996adbcb5f9e))

* chore: Update release workflow to trigger on pull requests instead of pushes ([`e0f3f5c`](https://github.com/LevyMatan/version_finder/commit/e0f3f5ccc9c906c25764a219f6276acc1750c817))

* chore: Update download-artifact action to v4 ([`98abd4f`](https://github.com/LevyMatan/version_finder/commit/98abd4ffcaf7e9f87acaf16ba1128c42e83aecea))

* chore: Update release workflow to use latest version of Node.js and npm ([`ebf1156`](https://github.com/LevyMatan/version_finder/commit/ebf11562184548c3df0bacf991ddaa374e4b83ad))

* chore: Update release workflow to list build directory and current directory ([`d563235`](https://github.com/LevyMatan/version_finder/commit/d563235d72267224b7916570331f5ba5d936e748))

* chore: Update release workflow to use GH_TOKEN instead of GITHUB_TOKEN ([`a3ccb7a`](https://github.com/LevyMatan/version_finder/commit/a3ccb7a0083e21d5191e4cf1112a8a1859decfe3))

* chore: Update release workflow to build and publish Linux and macOS packages ([`7b021cb`](https://github.com/LevyMatan/version_finder/commit/7b021cbe221a860fff306b1f3e8120d824e3f514))

* chore: Upgrade npm to version 9.5.1 ([`1c71582`](https://github.com/LevyMatan/version_finder/commit/1c715826e73d0fd98070fb0289f3d70258e740c3))

* chore: Update release workflow to build and publish Linux and macOS packages ([`4766e63`](https://github.com/LevyMatan/version_finder/commit/4766e63bc6d2cfc26e4caa552da55a829cc9c9e6))

* chore: Update npm dependencies and package.json for VersionFinder Electron app ([`5a81c5c`](https://github.com/LevyMatan/version_finder/commit/5a81c5c2b4188b0fd40cb0816e15e8827fac5aaf))

* chore: Update npm dependencies and package.json for VersionFinder Electron app ([`bb85ada`](https://github.com/LevyMatan/version_finder/commit/bb85adaeaa8c69399f0b768ddd3cac32d3843390))

* chore: Update release workflow to build and publish Linux and macOS packages ([`41f8ba5`](https://github.com/LevyMatan/version_finder/commit/41f8ba53b96eb6a5928f86d6292daa3b6d3961b5))

* chore: Update package.json for VersionFinder Electron app ([`ab24d6b`](https://github.com/LevyMatan/version_finder/commit/ab24d6b6ac9055424eacc484903851485d4c5119))

* chore: Update CSS styles for better alignment and readability ([`7dfc8a0`](https://github.com/LevyMatan/version_finder/commit/7dfc8a01a5984159ab54a3f5092dff9e63f98fcf))

* chore: Remove duplicate branches in VersionFinder ([`a5c39f2`](https://github.com/LevyMatan/version_finder/commit/a5c39f2fcbe2b074df631702e828d433e49b84da))

* chore: Reset form and disable input fields when changing repository in renderer.js ([`3dee329`](https://github.com/LevyMatan/version_finder/commit/3dee329cecf7b5025ed68295d9605e89c6b695e8))

* chore: Clear lists and result paragraph when changing repository in renderer.js ([`827c281`](https://github.com/LevyMatan/version_finder/commit/827c2814b7405e9519d91ae4c88c30fdc4b8175d))

* chore: Update app icon path in main.js ([`f3bf909`](https://github.com/LevyMatan/version_finder/commit/f3bf90972a06f8e89cb2fb944f10acb36fd5bec6))

* chore: Update main.js to conditionally open DevTools based on environment variable ([`3da0420`](https://github.com/LevyMatan/version_finder/commit/3da0420e4284824d5ba65411865e53c8c6f77ea5))

* chore: Update .gitignore and package.json for VersionFinder Electron app ([`8cd4f92`](https://github.com/LevyMatan/version_finder/commit/8cd4f926214d6bbe5b8fa50ef3a62b5655ba5092))

* chore: Update main.js to include app icon and open DevTools on startup ([`580ded0`](https://github.com/LevyMatan/version_finder/commit/580ded029e1967f3a13bed0d723c6ef3ffb39b14))

* chore: Update .gitignore and package.json for VersionFinder Electron app ([`7205ed9`](https://github.com/LevyMatan/version_finder/commit/7205ed9338641b2a90f3062a3fd72d5e4a166b10))

* chore: Refactor renderer.js to improve code organization and remove unnecessary comments ([`04f47da`](https://github.com/LevyMatan/version_finder/commit/04f47da2f01722e053082544d95c21e92f4ab98d))

* chore: Update npm dependency to latest stable version ([`666f376`](https://github.com/LevyMatan/version_finder/commit/666f376fd833a408ed8d5c65941606cf901303e6))

* chore: Update Version Finder CLI script and add installation instructions for Electron app ([`de5b75f`](https://github.com/LevyMatan/version_finder/commit/de5b75fdbe1aa0a3b8927be29e5058c88ce94a65))

* chore: Remove deprecated GUI code and Electron preload script ([`c7f35a3`](https://github.com/LevyMatan/version_finder/commit/c7f35a3dac1a708abeda645aef345c4ff1f7b8b8))

* chore: Update searchVersion function to handle cases when there are no submodules in the repository ([`03ad45a`](https://github.com/LevyMatan/version_finder/commit/03ad45add1223270dc1a5441d721edc8fbee2180))

* chore: Fix formatting issue in renderer.js ([`c554c9f`](https://github.com/LevyMatan/version_finder/commit/c554c9f3e3214ace7161750b17c27531c30cc7a9))

* chore: Update repository initialization process to include submodules and improve error handling ([`e7928f5`](https://github.com/LevyMatan/version_finder/commit/e7928f50228983678613bd4187a551faafaa1d39))

* chore: Update commit-sha input with default value of "HEAD~1" ([`f645b07`](https://github.com/LevyMatan/version_finder/commit/f645b072184cf02ebdac6bb41b5cdf37c62dbd2f))

* chore: Update commit-sha input with default value of "HEAD~1" ([`ed08ff9`](https://github.com/LevyMatan/version_finder/commit/ed08ff9b0dd8b969a2f08c3e446a2f4914bcb6f5))

* chore: Update sendSearchVersion function to handle cases when there are no submodules in the repository ([`f43e28c`](https://github.com/LevyMatan/version_finder/commit/f43e28c6d99d1956716926c9df39d11207ac858c))

* chore: Disable submodule input when there are no submodules in the repository ([`f9d4a29`](https://github.com/LevyMatan/version_finder/commit/f9d4a295485eed8c607b95a34c3674536c887fe2))

* chore: Refactor get_sha_of_first_commit_including_target method to handle submodules and return the SHA of the first commit including the target ([`55943bd`](https://github.com/LevyMatan/version_finder/commit/55943bdd6d081062cb32fe447e5898efb2d5331c))

* chore: Add version_finder.py for submodule and branch management ([`a431286`](https://github.com/LevyMatan/version_finder/commit/a431286dd8c179a684994383157a600ce693ef46))

* chore: Update README.md with project details and usage instructions ([`4b2b18b`](https://github.com/LevyMatan/version_finder/commit/4b2b18bd31a76d620f1a5afecbec27d6f2a515c1))

### Features

* feat(ci): Add versioning workflow ([`a6be5fe`](https://github.com/LevyMatan/version_finder/commit/a6be5fe2036dce0de4e49bfae566444469176f82))

* feat(versioning): Add semantic release ([`137fd5a`](https://github.com/LevyMatan/version_finder/commit/137fd5ab3200123b71e203f05ab76d191a904722))

* feat: Update search pattern in version finder to use selected option ([`c27121c`](https://github.com/LevyMatan/version_finder/commit/c27121c23d785428c1c22510e8821a5c940f3375))

* feat: Add settings button to index.html and create settings.html and settings.js files ([`0fd896c`](https://github.com/LevyMatan/version_finder/commit/0fd896c44a2e8b1fdfb638d3b451e2a344462c42))

* feat: Add error alert placeholder to index.html ([`d89680c`](https://github.com/LevyMatan/version_finder/commit/d89680c8a5cf9e5e876afdc266bc659616c0c3ed))

* feat: Add conditional check for valid first commit in findFirstCommit function ([`9df719b`](https://github.com/LevyMatan/version_finder/commit/9df719b767dfbd689e5c242f053600d06617dbea))

### Unknown

* Refactor version retrieval logic to use dynamic search pattern in main.js ([`7e6682d`](https://github.com/LevyMatan/version_finder/commit/7e6682dd171724f7689c48b1fe50aa39096eb6a7))

* Set default search pattern to underscore ([`942d654`](https://github.com/LevyMatan/version_finder/commit/942d6543e445b38a76466cd3d142d74032b5a5ea))

* Refactor header in index.html for improved accessibility and semantics ([`a942960`](https://github.com/LevyMatan/version_finder/commit/a942960419e8b64238395ebf7eed5239349de31d))

* Apply JS format using prettier ([`c11b5d2`](https://github.com/LevyMatan/version_finder/commit/c11b5d251b48a15c52a6ceaacec3f6fb98c39177))

* Update style.css and main.js for centered heading and add top margin/padding to h1 ([`234b9a7`](https://github.com/LevyMatan/version_finder/commit/234b9a7cd76276d913bf58ea1f3914c63579ae69))

* Update LinkedIn link color and remove default underline ([`6d23a8f`](https://github.com/LevyMatan/version_finder/commit/6d23a8f46b69a6a0b9c8629ad74e78132a16f3e1))

* Merge pull request #14 from LevyMatan:feature/add-setting-control

Feature/add-setting-control ([`9a21177`](https://github.com/LevyMatan/version_finder/commit/9a211773ba03a167f073051c83fdaed7c3b4ff58))

* Merge pull request #13 from LevyMatan:feature/error-notifier

Feature/error-notifier ([`2d9875c`](https://github.com/LevyMatan/version_finder/commit/2d9875c65a9a46e57218a6677f3e987421277ad9))

* Fix error handling in VersionFinder class ([`a532c47`](https://github.com/LevyMatan/version_finder/commit/a532c47fa26dcea6038df33647fd63f89b0d8ae6))

* feature: reduce log data for performance ([`38707b3`](https://github.com/LevyMatan/version_finder/commit/38707b37dd7f6df918e7395ae4bd582bbfb3cb3c))

* feature: improve repo browser response time ([`32b25a6`](https://github.com/LevyMatan/version_finder/commit/32b25a66e3ceac063afc9f06b214ad999304b059))

* feature: Update modal dialog class to scrollable ([`e183db0`](https://github.com/LevyMatan/version_finder/commit/e183db04210f1c6587155b7fbf3dcbf43bb38c7c))

* Merge pull request #12 from LevyMatan:feature/binary-search-commits

Use binary search instead of linear search ([`44eabc1`](https://github.com/LevyMatan/version_finder/commit/44eabc16b86a1a7d5756759784f1e1f8cf293773))

* Use binary search instead of linear search ([`8ffdb3e`](https://github.com/LevyMatan/version_finder/commit/8ffdb3e184d6b90cf081dab53c527ce911e29b31))

* Merge pull request #11 from LevyMatan:feature/add-loading-animation

Feature/add-loading-animation ([`55d66c6`](https://github.com/LevyMatan/version_finder/commit/55d66c626208dc4ad19b3e7cb79a8d110271a4f9))

* Version 1.1.0 ([`7d61051`](https://github.com/LevyMatan/version_finder/commit/7d6105127c60c2ca6e5f04a2108091572a336de5))

* Refactor version_finder.js to use async/await for executing git commands ([`111d5d0`](https://github.com/LevyMatan/version_finder/commit/111d5d0aaf90022fc030b225ff371f36f0c713c8))

* Version: 1.0.1 ([`8f421e4`](https://github.com/LevyMatan/version_finder/commit/8f421e4733bc078d26573e8509260033869f4041))

* Refactor version_finder.js to use regex for matching commit messages ([`9b9c743`](https://github.com/LevyMatan/version_finder/commit/9b9c743f294208daed1df50f8848396a237133eb))

* Add copy to clipboard button ([`b0be72a`](https://github.com/LevyMatan/version_finder/commit/b0be72ad2a0d363a67944567f9b2d81075d24680))

* Merge pull request #7 from LevyMatan:feature/improve-results

Feature/improve-results ([`794b31e`](https://github.com/LevyMatan/version_finder/commit/794b31ec5c4253423785ceb5202ac9d9608c29ae))

* Update CSS to add hover effect to clickable SHA elements ([`c74fa77`](https://github.com/LevyMatan/version_finder/commit/c74fa7748099d2a3bfee90071d75bf9d20dd9c03))

* debug: display current dir after artifact downloaded ([`df1f5ed`](https://github.com/LevyMatan/version_finder/commit/df1f5ed4abfac2d26ccf2d1937514515ee752ef5))

* Merge pull request #6 from LevyMatan:release-action

Pucblish packages ([`ad6d57c`](https://github.com/LevyMatan/version_finder/commit/ad6d57ce8dbdebacab3ecece477162be31a98b81))

* debug: print node and npm versions ([`df89588`](https://github.com/LevyMatan/version_finder/commit/df89588d4cfa878c3f04d70c45953175d46458c5))

* Merge pull request #5 from LevyMatan:release-action

chore: Update npm dependencies and package.json for VersionFinder Electron app ([`667f103`](https://github.com/LevyMatan/version_finder/commit/667f103b3b57a187a65958d9c06586bbbde88098))

* Merge remote-tracking branch 'origin/main' into release-action ([`6fea326`](https://github.com/LevyMatan/version_finder/commit/6fea326809837e4566cbba549419e615c3f259e6))

* Merge pull request #4 from LevyMatan/release-action

chore: Update release workflow to build and publish Linux and macOS p… ([`260e760`](https://github.com/LevyMatan/version_finder/commit/260e7604f1bbc89a799c76a56378681410d6a2b0))

* Merge pull request #3 from LevyMatan:dev-mode

chore: Update main.js to conditionally open DevTools based on environment variable ([`42bc8f6`](https://github.com/LevyMatan/version_finder/commit/42bc8f66caeb7a180fe9a373c2ccebcdd9431ddd))

* Nvidia style ([`688efca`](https://github.com/LevyMatan/version_finder/commit/688efca0d3c956712bf32d338084b58268c781f7))

* Use bootstrap instead of materilized ([`9c69507`](https://github.com/LevyMatan/version_finder/commit/9c6950729e8dc02325027f8958928a0ed7cd8f14))

* Merge pull request #2 from LevyMatan:new_main

Start Electron version of the app ([`421d6f1`](https://github.com/LevyMatan/version_finder/commit/421d6f1cdf28ed2ff896fa2da1c2395bedec203b))

* Merge remote-tracking branch 'origin/main' into new_main ([`e715163`](https://github.com/LevyMatan/version_finder/commit/e71516389ce81fb78eea98c4af4f966a702a1530))

* Refactor unitests.py to use consistent formatting for the main test runner ([`6692a28`](https://github.com/LevyMatan/version_finder/commit/6692a28ba032b93a84621b1b47ecdb45b28f5eeb))

* Improve comments ([`0d0efc2`](https://github.com/LevyMatan/version_finder/commit/0d0efc20ec540e75276e173d51bb0aa3a8c444b3))

* Refactor TestVersionFinder to assert commit is None ([`45b99bb`](https://github.com/LevyMatan/version_finder/commit/45b99bb67d8181e4643f1b68be5dd7e2eda64ff9))

* Start Electron version of the app ([`b3da2d6`](https://github.com/LevyMatan/version_finder/commit/b3da2d6f7cfb37abe90d06ee5e4cc42a01d49c0a))

* Refactor .gitignore to exclude __pycache__/** ([`e042fbf`](https://github.com/LevyMatan/version_finder/commit/e042fbf28a54d56aa52f71367bb235b2fee73ac4))

* Refactor VersionFinder class to remove `HEAD -> <current_branch>` branch from branches list ([`3a9dc40`](https://github.com/LevyMatan/version_finder/commit/3a9dc40145184b2d9d1b416bf580fc0687d59f5e))

* Add unit tests for VersionFinder class ([`da17d8b`](https://github.com/LevyMatan/version_finder/commit/da17d8b2c39900636b96854637539d4d4e3e1dfe))

* Refactor is_valid_commit_sha method to handle optional submodule parameter ([`2f5d86e`](https://github.com/LevyMatan/version_finder/commit/2f5d86e4aa15c5b938fa2648535aa146dca562bc))

* Add GUI option ([`d5bc189`](https://github.com/LevyMatan/version_finder/commit/d5bc1893ddd6ad6fabf309c37f3864e5c5fc1392))

* Add JS variant for the version_finder ([`bf663e2`](https://github.com/LevyMatan/version_finder/commit/bf663e2e532856c1b2a1533e965a72ca0340b5ee))

* Refactor VersionFinder class to handle submodules and improve error handling ([`b5cfcbd`](https://github.com/LevyMatan/version_finder/commit/b5cfcbdfdf0ebd73f309f392e2bc7b1cc1a34454))

* use CWD for subprocess ([`9dee32d`](https://github.com/LevyMatan/version_finder/commit/9dee32dab20ddfe152b402339d481d76d201e06b))

* Fix typo ([`a15f243`](https://github.com/LevyMatan/version_finder/commit/a15f243d229767847eae98ec05b8daf203f38f5a))

* Refactor version_finder.py to handle cases where no version is found in the logs ([`0632e81`](https://github.com/LevyMatan/version_finder/commit/0632e81710b39c40867d33b4660bc0b907512909))

* find commit message with Version: ([`5e4cf7e`](https://github.com/LevyMatan/version_finder/commit/5e4cf7e8cacbd85c6ef5a0d2a44291966c39569d))

* Refactor git log command to show all logs until the commit in reverse order ([`3316bbe`](https://github.com/LevyMatan/version_finder/commit/3316bbebbc61c4e8c659a5e9a46021dc0c541310))

* Refactor get_sha_of_first_commit_including_target method to handle submodules and remove debug print statement ([`c856f0e`](https://github.com/LevyMatan/version_finder/commit/c856f0e1add1ae34466018e6a25e0132c619ecab))

* Refactor get_sha_of_first_commit_including_target method to handle submodules and remove debug print statement ([`de2cfb8`](https://github.com/LevyMatan/version_finder/commit/de2cfb800b89cdd968adf68304690a3276d974d0))

* Refactor get_sha_of_first_commit_including_target method to handle submodules and remove debug print statement ([`1f748d4`](https://github.com/LevyMatan/version_finder/commit/1f748d4a161611db1853f276503afcc945afda9c))

* Refactor get_sha_of_first_commit_including_target method to handle submodules and remove debug print statement ([`74f1555`](https://github.com/LevyMatan/version_finder/commit/74f1555dd345e80c2e0c7e7ada497aa0a9c261c0))

* Refactor __get_pointer_to_submodule method to handle branch parameter and submodule updates ([`fa17ccf`](https://github.com/LevyMatan/version_finder/commit/fa17ccf6ea183be038e2c76b27675948c1612e50))

* Refactor get_sha_of_first_commit_including_target method to handle submodules and print the SHA of the first commit including the target ([`e160e7a`](https://github.com/LevyMatan/version_finder/commit/e160e7aac7ba0c6d2728c6e8fd94164ab20bd2e7))

* Refactor get_sha_of_first_commit_including_target method to handle submodules ([`d21ee19`](https://github.com/LevyMatan/version_finder/commit/d21ee1972373031e1bdce0c53fdacc9b21bc5577))

* Initial commit ([`4f087ef`](https://github.com/LevyMatan/version_finder/commit/4f087efc9c1c27b49ba1f373c4b810284abab2a0))

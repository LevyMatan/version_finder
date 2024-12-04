# CHANGELOG


## v1.0.0 (2024-12-04)

### Bug Fixes

- Add test.txt file with "Hello World!" content
  ([`a78c10a`](https://github.com/LevyMatan/version_finder/commit/a78c10ae4a1baacdd73698dcc1791aba458e9e73))

- Adjust the file path
  ([`cf1feb0`](https://github.com/LevyMatan/version_finder/commit/cf1feb05297d18bf1e02f1445575904a891568a0))

- Clear branch and submodule input fields in resetForm function
  ([`326e24d`](https://github.com/LevyMatan/version_finder/commit/326e24d60aef96309ac7f6dfb40add56248a7b51))

- Linux packaging command
  ([`d75c076`](https://github.com/LevyMatan/version_finder/commit/d75c0764d56a5ef2570d442ef08e43dd4a4db4d8))

- Remove unused mainWindow.versionFinder property
  ([`a1c7404`](https://github.com/LevyMatan/version_finder/commit/a1c74049e0b09d1a106cf53f849fb0c6dde98d0d))

- Submodules names
  ([`c5bdffd`](https://github.com/LevyMatan/version_finder/commit/c5bdffd8c1e534a4d0c3da068aa3e42653cedd5f))

- Update .releaserc message format
  ([`3753ea5`](https://github.com/LevyMatan/version_finder/commit/3753ea5c56d966b1c3105f55f7616e04fb56efec))

- Update VersionFinder constructor to use dynamic branch for validation
  ([`51835c2`](https://github.com/LevyMatan/version_finder/commit/51835c250598b9ec84895d1aac527288dc6f32bf))

The code changes update the VersionFinder constructor to use a dynamic branch for validation.
  Instead of hardcoding the branch name, the code now retrieves the branches from the repository and
  uses the first branch as the valid branch for initialization. This ensures that the VersionFinder
  object is properly initialized with a valid branch before any method is called that relies on its
  initialization state.

- **ci**: Actiavte .venv each step
  ([`ae891fd`](https://github.com/LevyMatan/version_finder/commit/ae891fdaf14ce3ce94b5360ef84359f5e20dcaa4))

- **ci**: Add github token to semantic-release
  ([`bcce626`](https://github.com/LevyMatan/version_finder/commit/bcce62639fc2ed33b0f7c56e9a04318bb09e1bdb))

- **ci**: Adjust the upload file path
  ([`af1a721`](https://github.com/LevyMatan/version_finder/commit/af1a721906f479f5d268a48d4d5c99a3623f0dc6))

- **ci**: Attach assets when a new Version commit is created
  ([`fbd2c19`](https://github.com/LevyMatan/version_finder/commit/fbd2c192ea5f031b51cf1c94230ebecc05f08abd))

- **ci**: Change secert name, Github doesnt allow to use GITHUB_TOKEN
  ([`c19308c`](https://github.com/LevyMatan/version_finder/commit/c19308c0def782320e4ece4be221178f177fc4a2))

- **ci**: Disable the "Release" workflow
  ([`3f8a9b6`](https://github.com/LevyMatan/version_finder/commit/3f8a9b6cc5463c5796c2f11cde05bfe89138ca5f))

- **ci**: Make the defualt branch to main
  ([`48bd0b3`](https://github.com/LevyMatan/version_finder/commit/48bd0b3cd9e7905ec81606c668464f49c1747053))

- **ci**: Npm version on github runner
  ([`8c5feb3`](https://github.com/LevyMatan/version_finder/commit/8c5feb301c0c468928a2d20f2972725632bbcec0))

- **ci**: Pass GH_TOKEN instead of GITHUB_TOKEN
  ([`5a90496`](https://github.com/LevyMatan/version_finder/commit/5a904960693a022c064f3c9e2c8496d17854bd7d))

- **ci**: Split release-and-build workflow
  ([`b08835d`](https://github.com/LevyMatan/version_finder/commit/b08835d91a60dae5607f07fb0a570779f0974215))

Divide responsability of the work flow to two distingished. The first, triggered by a push to
  master, will create a release using semantic-release. The second, triggered by a published
  release, will attach assets to it

- **ci**: Try to use virtual env
  ([`47e5519`](https://github.com/LevyMatan/version_finder/commit/47e5519ac170595a16a80d8e376b441e86fdbff1))

- **ci**: Used install-dev to get all dependencies
  ([`90553dc`](https://github.com/LevyMatan/version_finder/commit/90553dc8d9043da84d62811b9ef9fa8c53a36d32))

- **ci**: When a single platform build fails, continue with others.
  ([`49012d5`](https://github.com/LevyMatan/version_finder/commit/49012d54c003942abdb9c18a90db4d74bc0fd601))

- **commit-parser**: Adjust package location
  ([`655703e`](https://github.com/LevyMatan/version_finder/commit/655703efd61c8409b4daeb7e36e3bb23c1d362e7))

- **commit-parser**: Change project structre
  ([`98d7d80`](https://github.com/LevyMatan/version_finder/commit/98d7d8010bc2409d42478eec2e077285fb0ee8ab))

- **core**: :ambulance: boolean opeartion on a list even if with empty string return True.
  ([`24eb707`](https://github.com/LevyMatan/version_finder/commit/24eb7078f9b2b1d7e0c8e4bbf558e03813c8f1be))

Fixed the logic of handling an empty list when searching for commits

- **core**: :ambulance: change --is-ancestor to tun in submodule context
  ([`b833423`](https://github.com/LevyMatan/version_finder/commit/b8334237c2e4ef584bcfbf6ecc365e62b18bd430))

During the binary search to find the first commit in main repository to include a submodule commit,
  the comparison criteria which is --is-ancestor didn't run in the correct contect

- **core**: :ambulance: check for ancestor return value
  ([`a02ac0d`](https://github.com/LevyMatan/version_finder/commit/a02ac0d789f32ee71fa2b71a138ebee929eefb89))

The most annoying --is-ancestor will return an error when the first commit is not the ancestor of
  the second commit. When it is, it will return an empty BYTEs string!

- **core**: :bookmark: try and fix the semantic release flow
  ([`8dd7e76`](https://github.com/LevyMatan/version_finder/commit/8dd7e762492d49b3f4801048f6f121f970ab2d71))

- **core**: :bug: get commit between version with submodule
  ([`8530821`](https://github.com/LevyMatan/version_finder/commit/853082141ca5383c954dc986c48da300e1f2fba8))

Correct the git command sent once there is submodule involved

- **core**: :bug: more robust version pattern matching
  ([`9dcaffa`](https://github.com/LevyMatan/version_finder/commit/9dcaffa4dff6a2ec3df142e029c275de9a870e4f))

Use the --extended-regex option in git --grep to allow more accurate detection of versions

- **core**: :construction_worker: ci? semantic release it a mistake to split packages
  ([`95617c0`](https://github.com/LevyMatan/version_finder/commit/95617c058e7f2d4e4de98b9d22468ed09490c775))

- **core**: Error handling at: get_commit_sha_from_relative_string
  ([`196beb4`](https://github.com/LevyMatan/version_finder/commit/196beb4aa145e237c055c3af4379b19fe8b27791))

If the input commit sha is invalid, return a InvalidCommitError

- **core**: Fix binary search over the submodule pointers
  ([`d59ef68`](https://github.com/LevyMatan/version_finder/commit/d59ef6854513c887b659b4cae856aee9513ce53f))

- Add debug for the search - Correct the logic, adjust the is_ancestor criteria

- **core**: Fix getting the next version
  ([`3be55e9`](https://github.com/LevyMatan/version_finder/commit/3be55e998c2b40c7a32402f1c626d226d8c30036))

- **core**: Install build before building
  ([`d77129f`](https://github.com/LevyMatan/version_finder/commit/d77129f8bb1ecfe88e71685a66306ebffeb9a178))

- **core**: Make search for version more robust
  ([`6b3b8cd`](https://github.com/LevyMatan/version_finder/commit/6b3b8cd5580ef0ef3a0e01d018be5742a21d5730))

- **core**: Make the pattern for version case insensetive
  ([`6b03e92`](https://github.com/LevyMatan/version_finder/commit/6b03e924e66811850fb0ae005ff94fae20d10fd5))

- **core**: Remove dir paramter for semantic release
  ([`4e33c8f`](https://github.com/LevyMatan/version_finder/commit/4e33c8f35e50543757b893d922fc5122028580b7))

This cause an issue when running in CI, as it runs from different directory

- **core**: Submodule binary search fix --is-ancestor call by ignoring the exception on this case
  ([`c6d7e07`](https://github.com/LevyMatan/version_finder/commit/c6d7e072d7bcf1b9848205aa91bddeb0b7864f1e))

- **core-cli-gui**: Use direct call to semntic-release
  ([`b9d15f1`](https://github.com/LevyMatan/version_finder/commit/b9d15f131f9c1f94dd9d108474f3f16e0698bcda))

- **core-cli-gui-ci**: Properly install custom_scope_commit_parser
  ([`179d251`](https://github.com/LevyMatan/version_finder/commit/179d2514c5384df8309b6ad094c923955d63eff3))

- **core-gui-cli-versioning**: Update all the porject file
  ([`267c8b8`](https://github.com/LevyMatan/version_finder/commit/267c8b816ca47a95ca21f1b5fb779a1bd060374f))

BREAKING CHANGE: now each module has its own version - Updated workflows with matching release flows
  - Add custom commit parser

- **Dist**: :green_heart: Only upload to PyPI when a new release is created
  ([`0412a7e`](https://github.com/LevyMatan/version_finder/commit/0412a7ec36566fd99d82e22ddb4d66799d3d62f5))

- **Dist**: :rocket: change name of package to comply with PyPI
  ([`4d44b3e`](https://github.com/LevyMatan/version_finder/commit/4d44b3ea9b441fa0d236aaa20e0a0a39a830a7ff))

since version-finder name is too similar to other projects, had to change the name, but usage will
  still be short name

- **Dist**: Fix dist path for the cli package
  ([`af60acd`](https://github.com/LevyMatan/version_finder/commit/af60acdf71c07a2d105794dfa2100c916638c3d2))

- **docs**: Update readme setup instructions
  ([`dd1b4b1`](https://github.com/LevyMatan/version_finder/commit/dd1b4b14a6f70a2b466abbba255a10beb0d45d13))

- **find_first_version_containing_commit**: Remove branch input
  ([`7d7b135`](https://github.com/LevyMatan/version_finder/commit/7d7b135866d3ef0820a8799ac7eda2f7b309ed90))

- **get_commit_surrounding_versions**: Find the version even if the commit is the version
  ([`83c9b0b`](https://github.com/LevyMatan/version_finder/commit/83c9b0b6e8b13608ca462aa5880a860dbdbaf86d))

When searching for the next version commit, make sure to include the current commit in the search

- **GUI**: :bug: Correctly collapse the sidebar
  ([`ba350e6`](https://github.com/LevyMatan/version_finder/commit/ba350e62f114c28c945c181a31ac0cfe5129932c))

- **GUI**: :lipstick: Make the App window bigger
  ([`ddd2e14`](https://github.com/LevyMatan/version_finder/commit/ddd2e14ebfac76da7171b504fe1529d3e56f142c))

- **GUI**: :package: Add icon asset to the package
  ([`7a110bc`](https://github.com/LevyMatan/version_finder/commit/7a110bc296dd643f48d46322ac164187291b9b19))

- **gui**: Adjust font size and entry width
  ([`e54ae90`](https://github.com/LevyMatan/version_finder/commit/e54ae906b755f44edd7a7212b4d157c0bdc90246))

- **GUI**: Don't convert string to SHA in the search function
  ([`90e8bbf`](https://github.com/LevyMatan/version_finder/commit/90e8bbfca7fd65587adc60760e13ffdfdc8e4fd7))

When evoking Search in the GUI, it first tries to convert a rational string to commit SHA. The issue
  is when a submodule is given, the conversion is not done with respect to it

- **gui**: Improve autocomplete
  ([`34d753a`](https://github.com/LevyMatan/version_finder/commit/34d753a65985b959bc8684a5e4d66161c67b4537))

- **gui**: Remove call to branch in find version API
  ([`708d386`](https://github.com/LevyMatan/version_finder/commit/708d3868e7aed43c824f3fcdd67110f1af63aa5e))

- **install**: Add missing dependency
  ([`12faedb`](https://github.com/LevyMatan/version_finder/commit/12faedb5e2c332980a7daab06e42f095ebc203ee))

- **lint**: Add jest and bootstrap globals
  ([`e513cae`](https://github.com/LevyMatan/version_finder/commit/e513cae7da7b5d2a678b0467af6c3b4a61d49854))

- **logging**: Remove the log file from repo
  ([`0c3aa76`](https://github.com/LevyMatan/version_finder/commit/0c3aa766f49747e5fa3bfda74b1b6333d626019a))

- **main**: :bug: set default path to cwd, fix cal to find version
  ([`4655005`](https://github.com/LevyMatan/version_finder/commit/4655005dcde097b6bd83971e464fd82e66d12561))

BREAKING CHANGE: When no path argument is given, set the repository path to the current working
  directory. This now complies with the --help message of the program. Add a call to
  update_repository with the branch argument before calling the find_first_version_containg_commit.

- **main**: Import the version finder class
  ([`b1a443c`](https://github.com/LevyMatan/version_finder/commit/b1a443c874690e9d1a5afbe00653bf2ef3accb17))

- **misc**: Ignore virtual env folder
  ([`b143512`](https://github.com/LevyMatan/version_finder/commit/b143512811e7539724e6c1d5807e1e9c16e93eb7))

- **semantic-release**: Fetch entire git repo when cloning
  ([`68632d7`](https://github.com/LevyMatan/version_finder/commit/68632d7283b42ea58502ff36d8c0fec81247e223))

- **submodule-list**: Handle empty list in renderer
  ([`4bfb415`](https://github.com/LevyMatan/version_finder/commit/4bfb415717d86347eefd68e5ef6e1bb21d079727))

- **submodules list**: Return empty list when no submodules
  ([`16e7675`](https://github.com/LevyMatan/version_finder/commit/16e7675e11705f0161d3b3847b6cce29f764428a))

BREAKING CHANGE: Instead returning a list with the value: "No submodules in Repo" return an empty
  list

- **test**: Change master to main
  ([`3374007`](https://github.com/LevyMatan/version_finder/commit/337400775303204ae976919db97978ede10681f7))

- **test**: Modify an existing file instead of creating a new file
  ([`4244c37`](https://github.com/LevyMatan/version_finder/commit/4244c3760a22df27b89633fc95408db25c75f55a))

- **test**: Reorder changing files to git init
  ([`ab00b5d`](https://github.com/LevyMatan/version_finder/commit/ab00b5dd02af05da0864bc674fbcd8f28fecd6e7))

- **test**: Rewrite the file
  ([`acbbd9b`](https://github.com/LevyMatan/version_finder/commit/acbbd9bae902a6862998f436852c89639f9ad7eb))

- **Tests**: :bug: Handle invalid commit case in get_commit_info
  ([`682f8d6`](https://github.com/LevyMatan/version_finder/commit/682f8d6f2eb32323de5855ab85471ec56b1daedf))

- **version**: Trigger a major bump
  ([`ca69f3b`](https://github.com/LevyMatan/version_finder/commit/ca69f3b487f94b365a9d29d41c5f9a2edbf86921))

BREAKING CHANGE: last PR had an error in the commit message which caused the major version not to
  increament.

- **versioning**: Fix the version reported
  ([`d318534`](https://github.com/LevyMatan/version_finder/commit/d318534ff056fb75f75475ae048f6b957e86024c))

- sync the way version is fetched - allow semantic versioning action to update the files to update
  automatically

- **versioning**: Update the release workflow
  ([`9d00b06`](https://github.com/LevyMatan/version_finder/commit/9d00b0660e8d3c9ec8c0ec5d04296686579e4cdd))

### Build System

- **Infra**: :heavy_plus_sign: Add pytest-xdist for DEV falvor
  ([`b1dcae3`](https://github.com/LevyMatan/version_finder/commit/b1dcae3b8359e88fdc538b492a64b692f8e3b9e2))

Add the package to allow parrallel run of unit tests

### Chores

- Add ability to add new search patterns in settings
  ([`216200d`](https://github.com/LevyMatan/version_finder/commit/216200d7918884d261e7d17fee6334056956a1dd))

- Add extra top space to primary button
  ([`b9690b5`](https://github.com/LevyMatan/version_finder/commit/b9690b5bb6b4bf24c7438579eaf4dc42897f7b5e))

- Add form validation and error handling to version finder form
  ([`197b4d9`](https://github.com/LevyMatan/version_finder/commit/197b4d9e1a343e8a39bfe57b2e9ee0fb96bc0f73))

- Add isRepoDirty method to check if the repository has uncommitted changes
  ([`670e0c0`](https://github.com/LevyMatan/version_finder/commit/670e0c04eeff92cbe63e3807e0b9188a60ba6032))

- Add logo and icons assests
  ([`aa6901e`](https://github.com/LevyMatan/version_finder/commit/aa6901e2c927451fe31d9b6abcd6df9e5729c9c0))

- Add require-await rule for linter
  ([`bb84824`](https://github.com/LevyMatan/version_finder/commit/bb84824981dd549c85d2c8132bcfa7816813f217))

- Add spinner modal for processing message
  ([`47e4737`](https://github.com/LevyMatan/version_finder/commit/47e47371b148978538eb475852ba80b432d8850c))

- Add unnecessary console.log statement in getLogs test
  ([`d8c54b1`](https://github.com/LevyMatan/version_finder/commit/d8c54b1d350ef10c860092c4954b4eba0cd8bcf3))

- Add version_finder.py for submodule and branch management
  ([`a431286`](https://github.com/LevyMatan/version_finder/commit/a431286dd8c179a684994383157a600ce693ef46))

- Clean code and comments
  ([`bf9e574`](https://github.com/LevyMatan/version_finder/commit/bf9e574df8df8d64953fb6a2bcd6fa0bc0071874))

- Clear lists and result paragraph when changing repository in renderer.js
  ([`827c281`](https://github.com/LevyMatan/version_finder/commit/827c2814b7405e9519d91ae4c88c30fdc4b8175d))

- Disable submodule input when there are no submodules in the repository
  ([`f9d4a29`](https://github.com/LevyMatan/version_finder/commit/f9d4a295485eed8c607b95a34c3674536c887fe2))

- Fix formatting issue in renderer.js
  ([`c554c9f`](https://github.com/LevyMatan/version_finder/commit/c554c9f3e3214ace7161750b17c27531c30cc7a9))

- Handle error fetching first commit SHA in version_finder.js
  ([`41dd959`](https://github.com/LevyMatan/version_finder/commit/41dd959dee1d195f7a84a9293a48dcc028378621))

- Refactor error handling in renderer.js and main.js
  ([`af7ade5`](https://github.com/LevyMatan/version_finder/commit/af7ade59b9fd1b5f1793c44b80a18339597f3e71))

- Refactor get_sha_of_first_commit_including_target method to handle submodules and return the SHA
  of the first commit including the target
  ([`55943bd`](https://github.com/LevyMatan/version_finder/commit/55943bdd6d081062cb32fe447e5898efb2d5331c))

- Refactor renderer.js to improve code organization and remove unnecessary comments
  ([`04f47da`](https://github.com/LevyMatan/version_finder/commit/04f47da2f01722e053082544d95c21e92f4ab98d))

- Refactor search pattern options creation in settings.js
  ([`894bb4b`](https://github.com/LevyMatan/version_finder/commit/894bb4bbe19d7881c90fcafd2da8c7c0018f97ec))

- Refactor searchVersion function to accept form object directly
  ([`cc0a93a`](https://github.com/LevyMatan/version_finder/commit/cc0a93a2fb01531d166271e6c11afd26a517667e))

- Refactor settings creation in main.js
  ([`58ef0f3`](https://github.com/LevyMatan/version_finder/commit/58ef0f3a7270171af68908a6eb1dbd51d2f9a66d))

- Refactor undoRepoSnapshot method in VersionFinder class
  ([`b0cad77`](https://github.com/LevyMatan/version_finder/commit/b0cad771953ff5f118d6405cb66b8cda256fef13))

- Refactor unit-tests getSubmodules and getBranches methods
  ([`59ec519`](https://github.com/LevyMatan/version_finder/commit/59ec519ca17c7701f7d81addafb911884bdf0f27))

- Refactor VersionFinder class and update getLogs method
  ([`93541be`](https://github.com/LevyMatan/version_finder/commit/93541bebc1709416fa89b150655be4d81c9f8daa))

Remove unnecessary parameter from getLogs method and refactor the VersionFinder class to improve
  code organization and readability.

- Refactor VersionFinder class to improve code organization and readability
  ([`54e2b22`](https://github.com/LevyMatan/version_finder/commit/54e2b22a6661541af301a2563255ec1a87051622))

- Refactor VersionFinder class to use async/await for restoring repository snapshot
  ([`b689519`](https://github.com/LevyMatan/version_finder/commit/b689519fd47f20cf2050036ed2b8bef74feb1159))

- Remove commented out code for launching demo modal
  ([`ef9db0a`](https://github.com/LevyMatan/version_finder/commit/ef9db0aee0f9aa6ede5ddb332eb712632149e2f4))

- Remove deprecated GUI code and Electron preload script
  ([`c7f35a3`](https://github.com/LevyMatan/version_finder/commit/c7f35a3dac1a708abeda645aef345c4ff1f7b8b8))

- Remove duplicate branches in VersionFinder
  ([`a5c39f2`](https://github.com/LevyMatan/version_finder/commit/a5c39f2fcbe2b074df631702e828d433e49b84da))

- Remove new line added to test.txt file in afterEach hook
  ([`5de0b9b`](https://github.com/LevyMatan/version_finder/commit/5de0b9b5d76232b17f103acc2baa5334260402be))

- Remove unused imports and update VersionFinder initialization
  ([`0873cef`](https://github.com/LevyMatan/version_finder/commit/0873cef8db316e3208019e85ee114d824cf00964))

- Reset form and disable input fields when changing repository in renderer.js
  ([`3dee329`](https://github.com/LevyMatan/version_finder/commit/3dee329cecf7b5025ed68295d9605e89c6b695e8))

- Split publish jobs
  ([`304685b`](https://github.com/LevyMatan/version_finder/commit/304685bfe3e6db65c1087a1a38c8996adbcb5f9e))

- Update .gitignore and package.json for VersionFinder Electron app
  ([`8cd4f92`](https://github.com/LevyMatan/version_finder/commit/8cd4f926214d6bbe5b8fa50ef3a62b5655ba5092))

- Update .gitignore and package.json for VersionFinder Electron app
  ([`7205ed9`](https://github.com/LevyMatan/version_finder/commit/7205ed9338641b2a90f3062a3fd72d5e4a166b10))

- Update .gitignore to ignore 'out/' directory
  ([`0e0a0b4`](https://github.com/LevyMatan/version_finder/commit/0e0a0b41db799fa955cc200ed97c237af13f7f63))

This commit updates the .gitignore file to ignore the 'out/' directory. This directory is typically
  used for output files generated during the build process and should not be tracked by version
  control.

- Update app icon path in main.js
  ([`f3bf909`](https://github.com/LevyMatan/version_finder/commit/f3bf90972a06f8e89cb2fb944f10acb36fd5bec6))

- Update build scripts to use correct icon paths
  ([`ee6ea65`](https://github.com/LevyMatan/version_finder/commit/ee6ea65a5d7e8b72e463fc6b4f63d845e974dab8))

- Update button style and position in index.html
  ([`c4cbfe0`](https://github.com/LevyMatan/version_finder/commit/c4cbfe0fb173e7fe4d6ee55997d08c92d57d0739))

- Update commit-sha input with default value of "HEAD~1"
  ([`f645b07`](https://github.com/LevyMatan/version_finder/commit/f645b072184cf02ebdac6bb41b5cdf37c62dbd2f))

- Update commit-sha input with default value of "HEAD~1"
  ([`ed08ff9`](https://github.com/LevyMatan/version_finder/commit/ed08ff9b0dd8b969a2f08c3e446a2f4914bcb6f5))

- Update CSS styles for better alignment and readability
  ([`7dfc8a0`](https://github.com/LevyMatan/version_finder/commit/7dfc8a01a5984159ab54a3f5092dff9e63f98fcf))

- Update download-artifact action to v4
  ([`98abd4f`](https://github.com/LevyMatan/version_finder/commit/98abd4ffcaf7e9f87acaf16ba1128c42e83aecea))

- Update firstCommitMessage and versionCommitMessage display in renderer.js
  ([`8bdac0e`](https://github.com/LevyMatan/version_finder/commit/8bdac0e437bc2271906a122a31c0ad492e7187cf))

- Update getLogs method to remove unnecessary parameter
  ([`c41af1c`](https://github.com/LevyMatan/version_finder/commit/c41af1cefb922e09eb04f00703d3449ef197a6b7))

- Update index.html to fix version display issue
  ([`d6f6d97`](https://github.com/LevyMatan/version_finder/commit/d6f6d97d1e354036bd686897b8d71e0b0bdca4e9))

- Update IPC event name for saving repository state, add comments, adjust saveRepoState also for
  clean repos
  ([`6e4c22e`](https://github.com/LevyMatan/version_finder/commit/6e4c22eebd6ce8c2438ea826850910275f28b08f))

- Update logger configurations dynamically
  ([`6ade626`](https://github.com/LevyMatan/version_finder/commit/6ade6262423a4ed6ff880dbb76219fc64cfc384e))

- Update main.js to conditionally open DevTools based on environment variable
  ([`3da0420`](https://github.com/LevyMatan/version_finder/commit/3da0420e4284824d5ba65411865e53c8c6f77ea5))

- Update main.js to include app icon and open DevTools on startup
  ([`580ded0`](https://github.com/LevyMatan/version_finder/commit/580ded029e1967f3a13bed0d723c6ef3ffb39b14))

- Update npm dependencies and package.json for VersionFinder Electron app
  ([`5a81c5c`](https://github.com/LevyMatan/version_finder/commit/5a81c5c2b4188b0fd40cb0816e15e8827fac5aaf))

- Update npm dependencies and package.json for VersionFinder Electron app
  ([`bb85ada`](https://github.com/LevyMatan/version_finder/commit/bb85adaeaa8c69399f0b768ddd3cac32d3843390))

- Update npm dependency to latest stable version
  ([`666f376`](https://github.com/LevyMatan/version_finder/commit/666f376fd833a408ed8d5c65941606cf901303e6))

- Update package.json for VersionFinder Electron app
  ([`ab24d6b`](https://github.com/LevyMatan/version_finder/commit/ab24d6b6ac9055424eacc484903851485d4c5119))

- Update README.md with project details and usage instructions
  ([`4b2b18b`](https://github.com/LevyMatan/version_finder/commit/4b2b18bd31a76d620f1a5afecbec27d6f2a515c1))

- Update release workflow to build and publish Linux and macOS packages
  ([`7b021cb`](https://github.com/LevyMatan/version_finder/commit/7b021cbe221a860fff306b1f3e8120d824e3f514))

- Update release workflow to build and publish Linux and macOS packages
  ([`4766e63`](https://github.com/LevyMatan/version_finder/commit/4766e63bc6d2cfc26e4caa552da55a829cc9c9e6))

- Update release workflow to build and publish Linux and macOS packages
  ([`41f8ba5`](https://github.com/LevyMatan/version_finder/commit/41f8ba53b96eb6a5928f86d6292daa3b6d3961b5))

- Update release workflow to list build directory and current directory
  ([`d563235`](https://github.com/LevyMatan/version_finder/commit/d563235d72267224b7916570331f5ba5d936e748))

- Update release workflow to trigger on pull requests instead of pushes
  ([`e0f3f5c`](https://github.com/LevyMatan/version_finder/commit/e0f3f5ccc9c906c25764a219f6276acc1750c817))

- Update release workflow to use GH_TOKEN instead of GITHUB_TOKEN
  ([`a3ccb7a`](https://github.com/LevyMatan/version_finder/commit/a3ccb7a0083e21d5191e4cf1112a8a1859decfe3))

- Update release workflow to use latest version of Node.js and npm
  ([`ebf1156`](https://github.com/LevyMatan/version_finder/commit/ebf11562184548c3df0bacf991ddaa374e4b83ad))

- Update repository initialization process to include submodules and improve error handling
  ([`e7928f5`](https://github.com/LevyMatan/version_finder/commit/e7928f50228983678613bd4187a551faafaa1d39))

- Update searchVersion function to handle cases when there are no submodules in the repository
  ([`03ad45a`](https://github.com/LevyMatan/version_finder/commit/03ad45add1223270dc1a5441d721edc8fbee2180))

- Update sendSearchVersion function to handle cases when there are no submodules in the repository
  ([`f43e28c`](https://github.com/LevyMatan/version_finder/commit/f43e28c6d99d1956716926c9df39d11207ac858c))

- Update settings.html to include additional information about version search pattern customization
  ([`3fefce2`](https://github.com/LevyMatan/version_finder/commit/3fefce2e165890536f750824b438913c8b42b5cf))

- Update settings.html to include Bootstrap bundle and settings.js
  ([`8fedaf2`](https://github.com/LevyMatan/version_finder/commit/8fedaf27864ef8d2dd7113564da5fe92a5df99c8))

- Update style.css and main.js for centered heading and add top margin/padding to h1
  ([`eda013d`](https://github.com/LevyMatan/version_finder/commit/eda013d6104afebfc621e103123b1d40a2cc08ef))

- Update Version Finder CLI script and add installation instructions for Electron app
  ([`de5b75f`](https://github.com/LevyMatan/version_finder/commit/de5b75fdbe1aa0a3b8927be29e5058c88ce94a65))

- Update workflows for manual semantic release and unit testing
  ([`816ba16`](https://github.com/LevyMatan/version_finder/commit/816ba1668f7159b3e45d3bb806cf093561968622))

This commit updates the workflows for manual semantic release and unit testing. The previous
  workflow 'manual-semantic-release.yml' has been deleted, and a new workflow
  'release-and-build.yml' has been added. Additionally, a new workflow 'unit-test.yml' has been
  added for running unit tests. These changes aim to improve the release process and ensure proper
  testing of the codebase.

- Update workflows to use ADMIN_PAT
  ([`ba049e8`](https://github.com/LevyMatan/version_finder/commit/ba049e88e6d16fad9522715de7268175743e92dd))

- Upgrade npm to version 9.5.1
  ([`1c71582`](https://github.com/LevyMatan/version_finder/commit/1c715826e73d0fd98070fb0289f3d70258e740c3))

- Use async/await for restoring repository snapshot
  ([`5cf1d90`](https://github.com/LevyMatan/version_finder/commit/5cf1d9061f5a98b7aa812310552f8a3be378e306))

- Use modal to display results
  ([`ff18aeb`](https://github.com/LevyMatan/version_finder/commit/ff18aeb4fbb3d35e75df1f9dd8b0caa203e3f48e))

- **ci**: Add comments to workflow
  ([`253da1e`](https://github.com/LevyMatan/version_finder/commit/253da1e4490e3b55c79602aee1ac8c3c7b446442))

- **ci**: Add debug for semantic-release action
  ([`c0911c8`](https://github.com/LevyMatan/version_finder/commit/c0911c8de937753f70929b636148e5ae147fc959))

- **ci**: Remove unused workflow
  ([`e40f14c`](https://github.com/LevyMatan/version_finder/commit/e40f14c4f570f84fd78bb804d61c3c7c7d48eac8))

- **ci**: Try to change the access key
  ([`46e4ae2`](https://github.com/LevyMatan/version_finder/commit/46e4ae2b3b0c2f6fd6cd80c2f5323ef83378b683))

- **ci**: Try to use an action for semantic-release
  ([`f2518ea`](https://github.com/LevyMatan/version_finder/commit/f2518eaaca3d18f6c69f87e719f1b005e94de292))

- **ci**: Update to version 4
  ([`53dc32d`](https://github.com/LevyMatan/version_finder/commit/53dc32dccc79902f1a193383e6697b0dd4b30032))

- **clean**: Remove unused files and update package.json
  ([`99b496f`](https://github.com/LevyMatan/version_finder/commit/99b496f546e713d01456729b91f0d9c4e21aa91f))

- **code clean**: Remove duplicated comments and catch phrases
  ([`1269a69`](https://github.com/LevyMatan/version_finder/commit/1269a69a42bb796b9d0b848e90ebc370e00369f4))

- **core**: :recycle: Move git operation to a git executer class
  ([`c868f50`](https://github.com/LevyMatan/version_finder/commit/c868f50faeb4aeefc0d94d5ef953c0110087539a))

- **debug**: Remove unused configuration
  ([`c1186a9`](https://github.com/LevyMatan/version_finder/commit/c1186a942651b6d48486d48b945d23a4619a5ae5))

- **format**: Apply prettier format for all files
  ([`6c5b713`](https://github.com/LevyMatan/version_finder/commit/6c5b7131859e7caf56b0ca6a3853ba54dd9f8d0b))

- **Infra**: :bricks: fix the pyproject.toml configurations
  ([`d39e8e9`](https://github.com/LevyMatan/version_finder/commit/d39e8e945434e856e77e71dcd337c8c0aba3abbf))

the exclude given a list instead of a comma separated string

- **Infra**: Semantic-release config files
  ([`9a99dd3`](https://github.com/LevyMatan/version_finder/commit/9a99dd32b44196a1c84d6e656efe1df1112adb35))

- **logs**: Add Winston log to package
  ([`267261a`](https://github.com/LevyMatan/version_finder/commit/267261ac13b92887b6720757ddf8a5b0e5135c43))

- **release**: 1.0.0 [skip ci]
  ([`a2e7ab1`](https://github.com/LevyMatan/version_finder/commit/a2e7ab121825e43579811b6e302ae00411ec8b5b))

# 1.0.0 (2024-06-21)

### Bug Fixes

* adjust the file path
  ([cf1feb0](https://github.com/LevyMatan/version_finder/commit/cf1feb05297d18bf1e02f1445575904a891568a0))
  * **ci:** Add github token to semantic-release
  ([bcce626](https://github.com/LevyMatan/version_finder/commit/bcce62639fc2ed33b0f7c56e9a04318bb09e1bdb))
  * **ci:** npm version on github runner
  ([8c5feb3](https://github.com/LevyMatan/version_finder/commit/8c5feb301c0c468928a2d20f2972725632bbcec0))
  * **ci:** pass GH_TOKEN instead of GITHUB_TOKEN
  ([5a90496](https://github.com/LevyMatan/version_finder/commit/5a904960693a022c064f3c9e2c8496d17854bd7d))
  * Clear branch and submodule input fields in resetForm function
  ([326e24d](https://github.com/LevyMatan/version_finder/commit/326e24d60aef96309ac7f6dfb40add56248a7b51))
  * submodules names
  ([c5bdffd](https://github.com/LevyMatan/version_finder/commit/c5bdffd8c1e534a4d0c3da068aa3e42653cedd5f))

### Features

* Add conditional check for valid first commit in findFirstCommit function
  ([9df719b](https://github.com/LevyMatan/version_finder/commit/9df719b767dfbd689e5c242f053600d06617dbea))
  * Add error alert placeholder to index.html
  ([d89680c](https://github.com/LevyMatan/version_finder/commit/d89680c8a5cf9e5e876afdc266bc659616c0c3ed))
  * Add settings button to index.html and create settings.html and settings.js files
  ([0fd896c](https://github.com/LevyMatan/version_finder/commit/0fd896c44a2e8b1fdfb638d3b451e2a344462c42))
  * **ci:** Add versioning workflow
  ([a6be5fe](https://github.com/LevyMatan/version_finder/commit/a6be5fe2036dce0de4e49bfae566444469176f82))
  * Update search pattern in version finder to use selected option
  ([c27121c](https://github.com/LevyMatan/version_finder/commit/c27121c23d785428c1c22510e8821a5c940f3375))
  * **versioning:** Add semantic release
  ([137fd5a](https://github.com/LevyMatan/version_finder/commit/137fd5ab3200123b71e203f05ab76d191a904722))

- **release**: 1.1.0 [skip ci]
  ([`f1963f0`](https://github.com/LevyMatan/version_finder/commit/f1963f008a9152ec78743ccd476090f739c078f8))

# [1.1.0](https://github.com/LevyMatan/version_finder/compare/v1.0.0...v1.1.0) (2024-06-22)

### Bug Fixes

* **logging:** remove the log file from repo
  ([0c3aa76](https://github.com/LevyMatan/version_finder/commit/0c3aa766f49747e5fa3bfda74b1b6333d626019a))

### Features

* **logging:** Add logger - with control through settings
  ([11988e0](https://github.com/LevyMatan/version_finder/commit/11988e0f2be18c82d2c1c90d38a26bd07111b7fa))
  * **logging:** Add open log file button at settings page
  ([3771f54](https://github.com/LevyMatan/version_finder/commit/3771f54a09f08c5f62423500170d216113106ff2))

- **release**: 2.0.0 [skip ci]
  ([`9cd808e`](https://github.com/LevyMatan/version_finder/commit/9cd808e2464f25a820db5433d82ff352db6cc48f))

# [2.0.0](https://github.com/LevyMatan/version_finder/compare/v1.1.0...v2.0.0) (2024-06-22)

* pref(ipc-comm)!: Improve preformance by changing the ipc communication.
  ([75609cb](https://github.com/LevyMatan/version_finder/commit/75609cbdecac9092eb052773ad8b95b75a88143f))

### BREAKING CHANGES

* The change in IPC (modyfing existing IPC) may break competability with imaginary third parties.

- **release**: 2.1.0 [skip ci]
  ([`f770f0a`](https://github.com/LevyMatan/version_finder/commit/f770f0a3aed650ca1e1d256631801f0b27d65b7e))

# [2.1.0](https://github.com/LevyMatan/version_finder/compare/v2.0.0...v2.1.0) (2024-06-25)

### Bug Fixes

* **main:** import the version finder class
  ([b1a443c](https://github.com/LevyMatan/version_finder/commit/b1a443c874690e9d1a5afbe00653bf2ef3accb17))

### Features

* Add check for uncommitted changes in VersionFinder initialization
  ([52a9f85](https://github.com/LevyMatan/version_finder/commit/52a9f85c01770aa3e331602dbaead4e3dadfa0c9))
  * Add validation for search pattern in VersionFinder
  ([44e7438](https://github.com/LevyMatan/version_finder/commit/44e7438e5d8e202b3cc1e2b674fed2a2f9638ac5))
  * **lint:** Add eslint
  ([e8b4920](https://github.com/LevyMatan/version_finder/commit/e8b4920b376d2b76042027b45c3ad30957743114))
  * **version-finder:** Initialize VersionFinder in the constructor to set the 'isInitialized' flag
  to false. This ensures that the VersionFinder object is properly initialized before any method is
  called that relies on its initialization state.
  ([27f4750](https://github.com/LevyMatan/version_finder/commit/27f475036625f65ab33feddd4578a441feadea61))

- **release-core**: 9.0.0
  ([`6bd31f9`](https://github.com/LevyMatan/version_finder/commit/6bd31f952c79d9c41c72b50257086677a2804f8e))

Automatically generated by python-semantic-release

- **test**: Add cases handling for uncommitted changes in versionFinder tests
  ([`a9954d4`](https://github.com/LevyMatan/version_finder/commit/a9954d45aba4044f5b4e6add78c537277b8ed64a))

- **test**: Add testcase for a git repo with changes
  ([`a2c89d6`](https://github.com/LevyMatan/version_finder/commit/a2c89d603e0890aa2dad0e85834a7078a2c1d6f1))

- **testing**: Add jest as dependency
  ([`0c379c7`](https://github.com/LevyMatan/version_finder/commit/0c379c77f24f2a2d24e6671c66297f2050b956a5))

- **Tests**: Add type annotations to test
  ([`2803050`](https://github.com/LevyMatan/version_finder/commit/2803050189c88a20cc8cda562a15257eae292cd0))

- **unit-test**: Add isDirty tests
  ([`fe1da94`](https://github.com/LevyMatan/version_finder/commit/fe1da9428c8a12d449cb5a2e7602853703624c3c))

- **unit-test**: Add saveRepoSnapshot and restoreRepoSnapshot methods to VersionFinder tests
  ([`01220b8`](https://github.com/LevyMatan/version_finder/commit/01220b8a148e8334bce0ac196bcc65baaf39ea42))

- **unit-test**: Update error message for unknown file in versionFinder test
  ([`441c102`](https://github.com/LevyMatan/version_finder/commit/441c1021d2a056fb1b8ba980147e09ffca186775))

- **version**: Update core version to 1.1.0
  ([`de913a0`](https://github.com/LevyMatan/version_finder/commit/de913a07eaeec835f2f3a11228c01cc213919814))

### Code Style

- :art: apply autopep8
  ([`532cb4f`](https://github.com/LevyMatan/version_finder/commit/532cb4ffd0cead93c221a5863be692f2d1090d29))

- :art: apply format
  ([`6893c37`](https://github.com/LevyMatan/version_finder/commit/6893c37d1317a34a7e65088ecc0ac769110884ab))

- **core**: Remove extra ident
  ([`ba81951`](https://github.com/LevyMatan/version_finder/commit/ba81951fd64384d052016d6eac98f7e1002f57f1))

- **GUI**: :art: remove comments
  ([`d60491d`](https://github.com/LevyMatan/version_finder/commit/d60491d41d779e67c59b7695e0ec2453b29758f1))

### Continuous Integration

- **debug**: Custom parsers
  ([`bccdec8`](https://github.com/LevyMatan/version_finder/commit/bccdec842b5b3272317266a07b0910f95d54689d))

- **Dist**: :package: Upload the release to PyPI
  ([`581cda1`](https://github.com/LevyMatan/version_finder/commit/581cda14447295099c77558fb3fbf0db893623c5))

- **Dist**: Upload to PyPI when ran manually
  ([`655cbcf`](https://github.com/LevyMatan/version_finder/commit/655cbcf8db67e29c8f246db284df839a0d3ca809))

- **release**: Enable the semantic release steps
  ([`b1f7a54`](https://github.com/LevyMatan/version_finder/commit/b1f7a549c0e54e0c4627b18d7dbd1074692f57c1))

### Documentation

- :memo: update installation instructions
  ([`bd1b052`](https://github.com/LevyMatan/version_finder/commit/bd1b052e27daf75915f3c9b41a4ed8ea168a67ee))

- Update installation instructions with download link
  ([`bde1015`](https://github.com/LevyMatan/version_finder/commit/bde1015b4b9a24df4a3bfc8eafec11d1aea9e04e))

The installation instructions in the README.md file have been updated to include a direct download
  link for the latest version of the app from the Releases page. Additionally, a note has been added
  to specify that the app is only available for macOS and Linux platforms.

- **API**: Update description of tasks
  ([`cf100b4`](https://github.com/LevyMatan/version_finder/commit/cf100b429445f2f62e6f2e32f1d7ec97e8c81ba9))

- **Infra**: :memo: update installation instruction with pip install option
  ([`beb2c35`](https://github.com/LevyMatan/version_finder/commit/beb2c35aeb14b952ed20d7e448c4994146c253cb))

- **readme**: Add latestest release link and installation instruction
  ([`78a6cf7`](https://github.com/LevyMatan/version_finder/commit/78a6cf70ee796ea8e1afb432233446c0d52a4e03))

### Features

- :goal_net: handle version not found error
  ([`d2a964c`](https://github.com/LevyMatan/version_finder/commit/d2a964cc42cb14c683ee6cdf7860a30ee0736fa2))

Create a new Error type to indicate when a version is not found when searching for commits between
  two versions

- :page_facing_up: Add MIT license
  ([`e1c0666`](https://github.com/LevyMatan/version_finder/commit/e1c06660cb1dcbc222bd03e57254c343618e1d09))

- Add check for uncommitted changes in VersionFinder initialization
  ([`52a9f85`](https://github.com/LevyMatan/version_finder/commit/52a9f85c01770aa3e331602dbaead4e3dadfa0c9))

The commit adds a check for uncommitted changes in the VersionFinder initialization process. If
  there are any uncommitted changes, a warning is logged and the `hasChanges` flag is set to `true`.
  This ensures that the repository's state is taken into account when performing operations that
  rely on a clean repository.

- Add commit search functionality and improve repository handling
  ([`90bdb3a`](https://github.com/LevyMatan/version_finder/commit/90bdb3a6bd404f2769d7269a33e1521136393483))

- Add new find_commits_by_text functionality in main - Improve remote repository handling with
  __has_remote check - Only fetch from remote when repository has remotes configured - Fix string
  formatting to use %s style in logging statements - Add type hint for Dict, Any in imports

- Add conditional check for valid first commit in findFirstCommit function
  ([`9df719b`](https://github.com/LevyMatan/version_finder/commit/9df719b767dfbd689e5c242f053600d06617dbea))

- Add error alert placeholder to index.html
  ([`d89680c`](https://github.com/LevyMatan/version_finder/commit/d89680c8a5cf9e5e876afdc266bc659616c0c3ed))

- Add settings button to index.html and create settings.html and settings.js files
  ([`0fd896c`](https://github.com/LevyMatan/version_finder/commit/0fd896c44a2e8b1fdfb638d3b451e2a344462c42))

- Add validation for search pattern in VersionFinder
  ([`44e7438`](https://github.com/LevyMatan/version_finder/commit/44e7438e5d8e202b3cc1e2b674fed2a2f9638ac5))

The code changes add validation for the search pattern in the VersionFinder class. It checks if the
  search pattern is a string and a valid regular expression. If the search pattern is not a string
  or not a valid regex, an error is thrown. This ensures that the search pattern is properly
  validated before performing any search operations.

- Update icons for macOS and Linux platforms
  ([`f899d0b`](https://github.com/LevyMatan/version_finder/commit/f899d0b527e64296199270c66a852374062c0a66))

- Update search pattern in version finder to use selected option
  ([`c27121c`](https://github.com/LevyMatan/version_finder/commit/c27121c23d785428c1c22510e8821a5c940f3375))

- **automation**: Add Makefile with basic commands
  ([`e005f08`](https://github.com/LevyMatan/version_finder/commit/e005f085fc828bdd3d87976fb24deebd711e4e64))

The commands are: test, coverage, format, lint, clean

- **branch**: Dont update repo to branch on each api
  ([`b4bf5a9`](https://github.com/LevyMatan/version_finder/commit/b4bf5a9a036840aebc91c9ce389a9ff1ef293a1b))

BREAKING CHANGE Now the user is required to call updated_repository with a branch as an input
  in-order to call task APIs

- **ci**: Add versioning workflow
  ([`a6be5fe`](https://github.com/LevyMatan/version_finder/commit/a6be5fe2036dce0de4e49bfae566444469176f82))

- **ci**: Allow manual trigger of release and coverage
  ([`7b6d9ce`](https://github.com/LevyMatan/version_finder/commit/7b6d9cef15b210217a209bcafcef7296a724d273))

- **ci**: Run CI
  ([`876f85d`](https://github.com/LevyMatan/version_finder/commit/876f85de5632f6a3b1d34d7fc948d0c703b3615d))

- **ci**: Upgrade setup-python to version 5
  ([`eddf625`](https://github.com/LevyMatan/version_finder/commit/eddf625029f5c6ef129224c2d75b1b20fc5b5deb))

- **cli**: Add unit tests
  ([`7a9d1ba`](https://github.com/LevyMatan/version_finder/commit/7a9d1ba2c2fa1d067d47ce93e053b3793e48f924))

- **cli**: Improve command line interface
  ([`e394b2f`](https://github.com/LevyMatan/version_finder/commit/e394b2fb2a7e0485a7e8e870f01aa8159395bb8f))

Add colors to prompts, to attract user for current selection More elegant and easy to choose Better
  completion to enter repository path

- **cli**: When searching for text, ask for optional submodule
  ([`087b1e7`](https://github.com/LevyMatan/version_finder/commit/087b1e723933c9adfe415d83a719ec33f667136e))

Also make the autocompleter match from middle

- **core**: :goal_net: improve error handling in VersionFinder
  ([`2103188`](https://github.com/LevyMatan/version_finder/commit/2103188258cfee2e4e8ced72e71962cd9bfb34a7))

- **core**: :sparkles: use Commit class as the main cargo of information in APIs
  ([`1467162`](https://github.com/LevyMatan/version_finder/commit/1467162d04c9f3c3c9bc83bedbdec7a88ffe2ffc))

Use the Commit class as the proper return value for all VersionFinder APIs (Tasks). Improve the
  information recealed to user in the CLI when trying to get a list of commit

BREAKING CHANGE: change return value of APIs from List[str] to List[Commit]

- **core**: :test_tube: Increase the version string finding
  ([`660db71`](https://github.com/LevyMatan/version_finder/commit/660db71086a303e94f70d5eb497d8d398b636947))

- **core**: Add get_version_of_commit
  ([`6bf4838`](https://github.com/LevyMatan/version_finder/commit/6bf4838bb8dddde8fa4a97b574c010e7316a3344))

- **core**: Add snapshot mechanisim for dirty repos
  ([`c015bc8`](https://github.com/LevyMatan/version_finder/commit/c015bc8764b61e36bd7ba89c48d76e2ec22a4350))

BREAKING CHANGE: The change introduced will stash any changes and save the current commit hash.
  After it finishes the operations, it restores all.

- **core**: Store repo state, if any checkout occures, the state is restored
  ([`3f41f6b`](https://github.com/LevyMatan/version_finder/commit/3f41f6bb6887bbb97d12c2e98920407828412d09))

29-branch-change-not-restored

- **cov**: Upload coverage report
  ([`cdbd6f6`](https://github.com/LevyMatan/version_finder/commit/cdbd6f68a14b45100373838c5cbccef1c3327081))

- **create test repo**: Create a complex repo with many commits
  ([`eb6aee9`](https://github.com/LevyMatan/version_finder/commit/eb6aee94b71dd5d6941a0f05bb6dfeba0e4fde15))

- **ErrorHandling**: :technologist: Git installation instruction when does not exist
  ([`2d29ad7`](https://github.com/LevyMatan/version_finder/commit/2d29ad7b3bf7ab63328a62f9f0e33f1a5715b832))

- **GitExecuter**: :sparkles: verify git installation
  ([`bd4f584`](https://github.com/LevyMatan/version_finder/commit/bd4f584a1d134d445c68d3adb26b9ef27e263f1d))

- **GUI**: :sparkles: Add place holder to entry fields
  ([`d21fdfa`](https://github.com/LevyMatan/version_finder/commit/d21fdfa60caee4231e11892a51e9caf053d33043))

- **GUI**: :sparkles: Add sidebar with task change ability
  ([`eba1065`](https://github.com/LevyMatan/version_finder/commit/eba1065c02d9821067e1173f6f8f85a6a233d613))

Still need to fix the collapse button

- **gui**: Add logger to the gui
  ([`324f505`](https://github.com/LevyMatan/version_finder/commit/324f50526237bf57d149532dd5e475303ea96e0c))

- **GUI**: Create a modern simple GUI to interact with VersionFinder
  ([`1aeb2d8`](https://github.com/LevyMatan/version_finder/commit/1aeb2d8a1660929789ea6b04319560d98c5eaf2b))

- Add autocomplete for branch and submodule - Add error logging for user - Initialize a
  versionFinder instance on chosen repo path

- **gui**: File dialog box deafult is current dir
  ([`65b46c0`](https://github.com/LevyMatan/version_finder/commit/65b46c0b2626aae6132368688a21da04221e823a))

- **gui**: Update repo on branch selection
  ([`b60ff56`](https://github.com/LevyMatan/version_finder/commit/b60ff561a7bb2b2143e9312a40b77ca5b20bbff1))

BREAKING CHANGE This change solve the misalignment with the core change which require the version
  finder instance to update the repo before sending tasks

- **Infra**: :boom: Separte the packages and versions
  ([`2e517b9`](https://github.com/LevyMatan/version_finder/commit/2e517b9815215999424a0a69216d16e5b6207ec0))

BREAKING CHANGE: who will be bumped?!

- **lint**: Add eslint
  ([`e8b4920`](https://github.com/LevyMatan/version_finder/commit/e8b4920b376d2b76042027b45c3ad30957743114))

- **logging**: Add logger - with control through settings
  ([`11988e0`](https://github.com/LevyMatan/version_finder/commit/11988e0f2be18c82d2c1c90d38a26bd07111b7fa))

- **logging**: Add open log file button at settings page
  ([`3771f54`](https://github.com/LevyMatan/version_finder/commit/3771f54a09f08c5f62423500170d216113106ff2))

- **misc**: Add cli debuger configuration to vscode
  ([`34792a5`](https://github.com/LevyMatan/version_finder/commit/34792a5df5da30708e8ff6e6015d4bea5dec25ea))

- **package**: Build a package in CI for each release
  ([`77cde95`](https://github.com/LevyMatan/version_finder/commit/77cde9557f1861a82e5b328cea51d36be8cb814f))

- **search by text**: Add search within a submodule
  ([`bed7c24`](https://github.com/LevyMatan/version_finder/commit/bed7c243899614abbc7d24d0c58c14c70e0a86c2))

BREAKING CHANGE: change the task paramter interface, removed the branch param

- **test**: Add test for __extract_version_from_message
  ([`1e5df57`](https://github.com/LevyMatan/version_finder/commit/1e5df57b7acf7ade8da9a2b9e14c07ddcd9580ef))

- **test**: Add unit testing
  ([`ebb1d1d`](https://github.com/LevyMatan/version_finder/commit/ebb1d1d4e3dfe9e21bd857b138ad5c22b90abd65))

- **version-finder**: Initialize VersionFinder in the constructor to set the 'isInitialized' flag to
  false. This ensures that the VersionFinder object is properly initialized before any method is
  called that relies on its initialization state.
  ([`27f4750`](https://github.com/LevyMatan/version_finder/commit/27f475036625f65ab33feddd4578a441feadea61))

- **versioning**: Add semantic release
  ([`137fd5a`](https://github.com/LevyMatan/version_finder/commit/137fd5ab3200123b71e203f05ab76d191a904722))

### Performance Improvements

- **Tests**: :zap: Improve tests run time by using parallel execution
  ([`9b43713`](https://github.com/LevyMatan/version_finder/commit/9b43713be90743e41d44e12a94b7d4e19f6c8e79))

### Refactoring

- Apply format to index.html
  ([`5767453`](https://github.com/LevyMatan/version_finder/commit/576745348f8132a294b74eb8e1c893d69ca9fd01))

- Files format
  ([`aab520a`](https://github.com/LevyMatan/version_finder/commit/aab520a742592a2c4cecff598d8fb3001ffa25c2))

- Improve logger.js by handling errors when parsing additional data
  ([`5ebae6a`](https://github.com/LevyMatan/version_finder/commit/5ebae6a3308a7c95df8f2ca68a451c7d76ac3aae))

The logger.js file has been updated to handle errors that may occur when parsing additional data.
  This ensures that any errors encountered during the formatting of additional arguments (splat) are
  caught and logged. This change improves the robustness of the logger functionality.

- Remove unnecessary assignment of false to hasChanges property in VersionFinder class
  ([`095c02a`](https://github.com/LevyMatan/version_finder/commit/095c02a3aed5862db21230e7876f2ea469ebc5fc))

- Update .gitignore to ignore .DS_Store file
  ([`99dc227`](https://github.com/LevyMatan/version_finder/commit/99dc2278144872324d59f3876dbe6571ba9dbd55))

The .gitignore file has been updated to ignore the .DS_Store file. This file is automatically
  created by macOS and can be safely ignored in the repository.

- Update icon paths in package.json and index.html
  ([`9711963`](https://github.com/LevyMatan/version_finder/commit/9711963fd6f29e572bff479e50fd4aaf9e3f4304))

The icon paths in the package.json and index.html files have been updated to use the new
  version-finder-icon.icns file. This ensures that the correct icon is displayed for the application
  on both macOS and Linux platforms.

- Update VersionFinder class to check repository dirtiness during initialization
  ([`6825575`](https://github.com/LevyMatan/version_finder/commit/6825575639f259d0862ff9d18421b352dcc2d451))

The `hasChanges` property in the VersionFinder class is now set by calling the `isRepoDirty` method
  during initialization. This ensures that the `hasChanges` property accurately reflects the
  repository's dirtiness. The unnecessary assignment of `false` to `hasChanges` has been removed.

- Update VersionFinder class to use async/await for checking repository dirtiness during
  initialization
  ([`7ca58d6`](https://github.com/LevyMatan/version_finder/commit/7ca58d6b6bd0ed9500711a061e9870d6c49a700a))

- **cli**: Remove unused import
  ([`d35b987`](https://github.com/LevyMatan/version_finder/commit/d35b98763421832cf2ce821e95c8e6a509ee81b7))

- **Infra**: :truck: split the project to 3 seperate apps
  ([`9b9b648`](https://github.com/LevyMatan/version_finder/commit/9b9b648a69cdb4e9570bf2f4d5b00e6be43fb79f))

### Testing

- **core**: :white_check_mark: add test to commit between versions method
  ([`d6f794d`](https://github.com/LevyMatan/version_finder/commit/d6f794dd72bda82134099d275cf7d904b3ec545a))

- **core**: :white_check_mark: tests for get_commit_info
  ([`8ef0cbb`](https://github.com/LevyMatan/version_finder/commit/8ef0cbbdf71e7bf49c35b23a62d6b5e7e811c177))

- **RepoGenerator**: :poop: make the test repo with submodule
  ([`083cf16`](https://github.com/LevyMatan/version_finder/commit/083cf16f3eaf4307ebed6f1193124cc766376d5e))

### BREAKING CHANGES

- **Infra**: Who will be bumped?!

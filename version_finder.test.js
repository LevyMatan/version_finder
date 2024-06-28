const path = require("path");
const { VersionFinder } = require("./version_finder");

describe("VersionFinder: Constructor", () => {
  let versionFinder;

  it("should initialize with default repository path", () => {
    versionFinder = new VersionFinder();
    expect(versionFinder.repositoryPath).toBe(process.cwd());
  });

  it("should throw an error if the provided path is not valid", () => {
    const invalidPath = "/path/that/does/not/exist";
    expect(() => {
      new VersionFinder(invalidPath);
    }).toThrow('The provided path "/path/that/does/not/exist" does not exist.');
  });

  it("should throw an error if the provided path is not a valid git repository", async () => {
    const noRepoPath = "/";
    const notRepoVersionFinder = new VersionFinder(noRepoPath);
    await expect(async () => {
      await notRepoVersionFinder.init();
    }).rejects.toThrow("The given path / is Not a git repository");
  });
});

describe("VersionFinder: Not initialized", () => {
  let versionFinderNotInitialized;

  beforeEach(() => {
    versionFinderNotInitialized = new VersionFinder();
  });

  it("should show the instance is not initialized", () => {
    expect(versionFinderNotInitialized.isInitialized).toBe(false);
  });

  it("should throw an error if trying to get submodules", () => {
    expect(() => versionFinderNotInitialized.getSubmodules()).toThrow(
      "VersionFinder is not initialized"
    );
  });

  it("should throw an error if trying to get branches", () => {
    expect(() => versionFinderNotInitialized.getBranches()).toThrow(
      "VersionFinder is not initialized"
    );
  });

  it("should throw an error if trying to get logs", async () => {
    await expect(
      versionFinderNotInitialized.getLogs("fake-branch")
    ).rejects.toThrow("VersionFinder is not initialized");
  });

  it("should throw an error if trying to get first commit SHA", async () => {
    await expect(
      versionFinderNotInitialized.getFirstCommitSha()
    ).rejects.toThrow("VersionFinder is not initialized");
  });

  it("should set the search pattern", () => {
    const searchPatternRegex = /Testing v\d+\.\d+\.\d+/;
    versionFinderNotInitialized.setSearchPattern(searchPatternRegex.toString());
    expect(versionFinderNotInitialized.searchPatternRegex.toString()).toBe(
      searchPatternRegex.toString()
    );
  });

  it("should throw an error if trying to set the search pattern with invalid regex", () => {
    const invalidSearchPattern = "Testing vd+.d+.d+";
    expect(() => {
      versionFinderNotInitialized.setSearchPattern(invalidSearchPattern);
    }).toThrow("The search pattern must be a valid regex.");
  });

  it("should throw an error if trying to set the search pattern with a string that is not a regex", () => {
    const invalidSearchPattern = "Testing v1.0.0";
    expect(() => {
      versionFinderNotInitialized.setSearchPattern(invalidSearchPattern);
    }).toThrow("The search pattern must be a valid regex.");
  });

  it("should throw an error if trying to set the search pattern with a number", () => {
    const invalidSearchPattern = 123;
    expect(() => {
      versionFinderNotInitialized.setSearchPattern(invalidSearchPattern);
    }).toThrow("The search pattern must be a string.");
  });
});

describe("VersionFinder: Initialized", () => {
  let versionFinder;

  beforeEach(async () => {
    versionFinder = new VersionFinder();
    await versionFinder.init();
  });

  it("should show the instance is initialized", () => {
    expect(versionFinder.isInitialized).toBe(true);
  });

  it("should get the submodules", async () => {
    const submodules = await versionFinder.getSubmodules();
    expect(submodules).toBeInstanceOf(Array);
  });

  it("should get the branches", async () => {
    const branches = await versionFinder.getBranches();
    expect(branches).toBeInstanceOf(Array);
  });

  it("should set the search pattern", () => {
    const searchPatternRegex = /Testing v\d+\.\d+\.\d+/;
    versionFinder.setSearchPattern(searchPatternRegex.toString());
    expect(versionFinder.searchPatternRegex.toString()).toBe(
      searchPatternRegex.toString()
    );
  });

  it("should check if branch is valid", async () => {
    const branches = await versionFinder.getBranches();
    const validBranch = branches[0];
    const invalidBranch = "fake-branch";
    const isValidBranch = await versionFinder.isValidBranch(validBranch);
    const isInvalidBranch = await versionFinder.isValidBranch(invalidBranch);
    expect(isValidBranch).toBe(true);
    expect(isInvalidBranch).toBe(false);
  });

  it("should check if submodule is valid", async () => {
    const invalidSubmodule = "fake-submodule";
    const isInvalidSubmodule = await versionFinder.isValidSubmodule(
      invalidSubmodule
    );
    expect(isInvalidSubmodule).toBe(false);
  });
});

describe("VersionFinder: Repo with changes", () => {
  let versionFinderWithChanges;

  beforeEach(async () => {
    // append a new line to this file
    const fs = require("fs");
    fs.writeFileSync(
      path.join(process.cwd(), "test.txt"),
      "I am a changed file!"
    );

    versionFinderWithChanges = new VersionFinder();
    await versionFinderWithChanges.init();
  });

  afterEach(() => {
    // remove the new line added to this file
    const fs = require("fs");
    fs.writeFileSync(path.join(process.cwd(), "test.txt"), "Hello World!");
  });

  it("should throw an error of uncommitted changes when calling getLogs", async () => {
    console.log("versionFinderWithChanges", versionFinderWithChanges);
    await expect(versionFinderWithChanges.getLogs("main")).rejects.toThrow(
      "The repository has uncommitted changes. Please commit or discard the changes before proceeding."
    );
  });

  it("should throw an error of uncommitted changes when calling getFirstCommitSha", async () => {
    const targetCommitHash = "f7f3f6d";
    const branchName = "main";
    const submoduleName = "submodule";
    await expect(
      versionFinderWithChanges.getFirstCommitSha(
        targetCommitHash,
        branchName,
        submoduleName
      )
    ).rejects.toThrow(
      "The repository has uncommitted changes. Please commit or discard the changes before proceeding."
    );
  });

  it("should throw an error of uncommitted changes when calling isValidCommitSha", async () => {
    const targetCommitHash = "f7f3f6d";
    const branchName = "main";
    const submoduleName = "submodule";
    await expect(
      versionFinderWithChanges.isValidCommitSha(
        targetCommitHash,
        branchName,
        submoduleName
      )
    ).rejects.toThrow(
      "The repository has uncommitted changes. Please commit or discard the changes before proceeding."
    );
  });

  it("should throw an error of uncommitted changes when calling getFirstCommitWithVersion", async () => {
    await expect(
      versionFinderWithChanges.getFirstCommitWithVersion("master", "test.txt")
    ).rejects.toThrow(
      "The repository has uncommitted changes. Please commit or discard the changes before proceeding."
    );
  });

  it("should indicate the repository is dirty", async () => {
    const isDirty = await versionFinderWithChanges.isRepoDirty(
      versionFinderWithChanges.git
    );
    expect(isDirty).toBe(true);
  });

  it("should saveRepoSnapshot and indicate repo is clean", async () => {
    await versionFinderWithChanges.saveRepoSnapshot();
    const isDirty = await versionFinderWithChanges.isRepoDirty(
      versionFinderWithChanges.git
    );
    expect(isDirty).toBe(false);
  });

  it("should saveRepoSnapshot and indicate repo is clean then restore", async () => {
    await versionFinderWithChanges.saveRepoSnapshot();
    const isDirty = await versionFinderWithChanges.isRepoDirty(
      versionFinderWithChanges.git
    );
    expect(isDirty).toBe(false);
    await versionFinderWithChanges.restoreRepoSnapshot();
    const isDirtyAfterRestore = await versionFinderWithChanges.isRepoDirty(
      versionFinderWithChanges.git
    );
    expect(isDirtyAfterRestore).toBe(true);
  });
});

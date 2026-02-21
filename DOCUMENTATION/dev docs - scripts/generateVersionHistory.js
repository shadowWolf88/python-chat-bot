
//run node generateVersionHistory.js
//paste output in indez (search for const APP_UPDATES)

const { execSync } = require("child_process");
const fs = require("fs");

// ===== CONFIG =====
const MAJOR_VERSION = 22; // change when needed
const OUTPUT_FILE = "appUpdates.js"; // set to null if you only want console output

// ===== GET GIT COMMITS =====
function getGitCommits() {
    const raw = execSync(
        'git log --pretty=format:"%H|%ad|%s" --date=short',
        { encoding: "utf8" }
    );

    return raw.split("\n").map(line => {
        const [hash, date, message] = line.split("|");
        return { hash, date, message };
    });
}

// ===== BUILD VERSION HISTORY =====
function buildVersionHistory(commits) {
    return commits.map((commit, index) => {
        const version = `${MAJOR_VERSION}.${commits.length - index}`;

        return {
            date: commit.date,
            version,
            title: commit.message,
            changes: [commit.message]
        };
    });
}

// ===== FORMAT OUTPUT =====
function formatOutput(updates) {
    return `const APP_UPDATES = ${JSON.stringify(updates, null, 4)};`;
}

// ===== MAIN =====
try {
    const commits = getGitCommits();
    const updates = buildVersionHistory(commits);
    const output = formatOutput(updates);

    if (OUTPUT_FILE) {
        fs.writeFileSync(OUTPUT_FILE, output);
        console.log(`✅ Version history written to ${OUTPUT_FILE}`);
    } else {
        console.log(output);
    }

} catch (err) {
    console.error("❌ Error generating version history:", err.message);
}
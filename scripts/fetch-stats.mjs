
// scripts/fetch-stats.mjs
//
// Fetches live GitHub data and renders it into custom SVGs:
//   1. Telemetry panel      — language distribution (REST API)
//   2. GitHub stats panel   — stars, commits, PRs, issues, contributed-to
//   3. Contribution graph   — rolling 12-month contribution chart (GraphQL)
//
// Required environment variables:
//   GITHUB_USERNAME
//   GITHUB_TOKEN
//
// Run:
//   GITHUB_TOKEN=xxx GITHUB_USERNAME=vanshkalawatia node scripts/fetch-stats.mjs

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

// --------------------------------------------------
// Repository paths
// --------------------------------------------------

// Resolve paths relative to this script instead of process.cwd().
// This makes the script reliable inside GitHub Actions.

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(SCRIPT_DIR, "..");

const repoPath = (...parts) => path.join(REPO_ROOT, ...parts);

// --------------------------------------------------
// Environment
// --------------------------------------------------

const USERNAME = process.env.GITHUB_USERNAME;
const TOKEN = process.env.GITHUB_TOKEN;

if (!USERNAME || !TOKEN) {
  console.error("Missing GITHUB_USERNAME or GITHUB_TOKEN environment variables.");
  process.exit(1);
}

const API = "https://api.github.com";
const GRAPHQL_API = "https://api.github.com/graphql";

const headers = {
  Authorization: `Bearer ${TOKEN}`,
  Accept: "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28",
};

const MAX_LANGUAGE_ROWS = 5;

// --------------------------------------------------
// Template and output paths
// --------------------------------------------------

const TELEMETRY_TARGETS = [
  {
    template: repoPath("assets", "templates", "telemetry-light.template.svg"),
    output: repoPath("assets", "telemetry.svg"),
  },
  {
    template: repoPath("assets", "templates", "telemetry-dark.template.svg"),
    output: repoPath("assets", "dark", "telemetry.svg"),
  },
];

const GITHUB_STATS_TARGETS = [
  {
    template: repoPath("assets", "templates", "github-stats-light.template.svg"),
    output: repoPath("assets", "github-stats.svg"),
  },
  {
    template: repoPath("assets", "templates", "github-stats-dark.template.svg"),
    output: repoPath("assets", "dark", "github-stats.svg"),
  },
];

const CONTRIBUTION_TARGETS = [
  {
    template: repoPath(
      "assets",
      "templates",
      "contribution-graph-light.template.svg"
    ),
    output: repoPath("assets", "contribution-graph.svg"),
  },
  {
    template: repoPath(
      "assets",
      "templates",
      "contribution-graph-dark.template.svg"
    ),
    output: repoPath("assets", "dark", "contribution-graph.svg"),
  },
];

// --------------------------------------------------
// REST API: repositories and languages
// --------------------------------------------------

async function getAllRepos() {
  let repos = [];
  let page = 1;

  while (true) {
    const res = await fetch(
      `${API}/users/${USERNAME}/repos?per_page=100&page=${page}&type=owner`,
      { headers }
    );

    if (!res.ok) {
      throw new Error(`Failed to fetch repositories: ${res.status}`);
    }

    const batch = await res.json();

    if (batch.length === 0) break;

    repos = repos.concat(batch);
    page++;
  }

  return repos.filter((repo) => !repo.fork);
}

async function getLanguagesForRepo(repoName) {
  const res = await fetch(
    `${API}/repos/${USERNAME}/${repoName}/languages`,
    { headers }
  );

  if (!res.ok) {
    console.warn(`  ! Skipped ${repoName} (${res.status})`);
    return {};
  }

  return res.json();
}

// --------------------------------------------------
// Language calculations
// --------------------------------------------------

function toPercentages(totals) {
  const totalBytes = Object.values(totals).reduce(
    (sum, bytes) => sum + bytes,
    0
  );

  if (totalBytes === 0) {
    return [];
  }

  const sorted = Object.entries(totals)
    .map(([lang, bytes]) => ({
      lang,
      pct: Math.round((bytes / totalBytes) * 1000) / 10,
    }))
    .sort((a, b) => b.pct - a.pct);

  const top = sorted.slice(0, MAX_LANGUAGE_ROWS);

  const otherPct =
    Math.round(
      sorted
        .slice(MAX_LANGUAGE_ROWS)
        .reduce((sum, language) => sum + language.pct, 0) * 10
    ) / 10;

  if (otherPct > 0) {
    top.push({ lang: "other", pct: otherPct });
  }

  return top;
}

// --------------------------------------------------
// GraphQL API
// --------------------------------------------------

async function graphql(query) {
  const res = await fetch(GRAPHQL_API, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    throw new Error(`GitHub GraphQL HTTP error: ${res.status}`);
  }

  const json = await res.json();

  if (json.errors) {
    throw new Error(
      `GraphQL error: ${JSON.stringify(json.errors)}. ` +
      "Check your token permissions. The token may need read:user scope."
    );
  }

  if (!json.data?.user) {
    throw new Error(`GitHub user not found: ${USERNAME}`);
  }

  return json.data;
}

async function getGithubStats() {
  const now = new Date();

  // Rolling 12-month contribution window.
  const from = new Date(now);
  from.setFullYear(from.getFullYear() - 1);

  const fromISO = from.toISOString();
  const to = now.toISOString();

  const query = `
    query {
      user(login: "${USERNAME}") {
        pullRequests {
          totalCount
        }

        openIssues: issues(states: OPEN) {
          totalCount
        }

        closedIssues: issues(states: CLOSED) {
          totalCount
        }

        repositoriesContributedTo(
          first: 1
          contributionTypes: [COMMIT, PULL_REQUEST, ISSUE]
        ) {
          totalCount
        }

        contributionsCollection(from: "${fromISO}", to: "${to}") {
          totalCommitContributions

          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
  `;

  const data = await graphql(query);
  const user = data.user;

  return {
    totalCommits:
      user.contributionsCollection.totalCommitContributions,

    totalPRs: user.pullRequests.totalCount,

    totalIssues:
      user.openIssues.totalCount +
      user.closedIssues.totalCount,

    contributedTo:
      user.repositoriesContributedTo.totalCount,

    calendarDays:
      user.contributionsCollection.contributionCalendar.weeks.flatMap(
        (week) => week.contributionDays
      ),
  };
}

// --------------------------------------------------
// Monthly contribution calculations
// --------------------------------------------------

function monthlyTotalsFromCalendar(days) {
  const buckets = {};

  for (const day of days) {
    const month = day.date.slice(0, 7);

    buckets[month] =
      (buckets[month] || 0) + day.contributionCount;
  }

  const months = Object.keys(buckets).sort();
  const last12 = months.slice(-12);

  return last12.map((month) => ({
    month,
    count: buckets[month],
  }));
}

// --------------------------------------------------
// SVG rendering: telemetry
// --------------------------------------------------

function buildLanguageRowsTelemetry(languages) {
  const MAX_BAR_WIDTH = 220;
  const MIN_BAR_WIDTH = 4;

  const topPct = Math.max(
    1,
    ...languages.map((language) => language.pct)
  );

  let bars = "";

  let yLabel = 108;
  let yBar = 116;
  let yPct = 123;

  const ROW_HEIGHT = 38;

  for (let i = 0; i < languages.length; i++) {
    const { lang, pct } = languages[i];

    const width = Math.max(
      MIN_BAR_WIDTH,
      Math.round((pct / topPct) * MAX_BAR_WIDTH)
    );

    const fillVar =
      i === 0 ? "var(--accent)" : "var(--bone)";

    const barClass = `g${i + 1}`;

    bars += `
      <text fill="var(--bone)" x="48" y="${yLabel}">
        ${lang.toLowerCase()}
      </text>

      <rect
        class="bar ${barClass}"
        x="48"
        y="${yBar}"
        width="${width}"
        height="6"
        fill="${fillVar}"
      />

      <text
        fill="var(--muted)"
        x="${48 + width + 10}"
        y="${yPct}"
        font-size="10"
      >${pct}%</text>
    `;

    yLabel += ROW_HEIGHT;
    yBar += ROW_HEIGHT;
    yPct += ROW_HEIGHT;
  }

  return bars.trim();
}

// --------------------------------------------------
// SVG rendering: GitHub statistics
// --------------------------------------------------

function buildLanguageBarsForStatsPanel(languages) {
  const MAX_BAR_WIDTH = 270;

  const topPct = Math.max(
    1,
    ...languages.map((language) => language.pct)
  );

  let rows = "";

  let y = 105;
  let yRect = 94;

  const ROW_HEIGHT = 36;

  for (let i = 0; i < languages.length; i++) {
    const { lang, pct } = languages[i];

    const width = Math.max(
      4,
      Math.round((pct / topPct) * MAX_BAR_WIDTH)
    );

    const growClass =
      i === 0 ? "grow" : `grow g${i + 1}`;

    rows += `
      <text x="548" y="${y}" font-size="10">
        ${lang.toUpperCase()}
      </text>

      <rect
        class="bar"
        x="660"
        y="${yRect}"
        width="${MAX_BAR_WIDTH}"
        height="12"
      />

      <rect
        class="fill ${growClass}"
        x="660"
        y="${yRect}"
        width="${width}"
        height="12"
      />
    `;

    y += ROW_HEIGHT;
    yRect += ROW_HEIGHT;
  }

  return rows.trim();
}

// --------------------------------------------------
// SVG rendering: contribution graph
// --------------------------------------------------

function buildContributionBars(monthly) {
  const CHART_LEFT = 48;
  const CHART_RIGHT = 952;
  const CHART_TOP = 60;
  const CHART_BOTTOM = 180;

  const maxCount = Math.max(
    1,
    ...monthly.map((month) => month.count)
  );

  const slot =
    (CHART_RIGHT - CHART_LEFT) /
    Math.max(1, monthly.length);

  const barWidth = slot * 0.55;

  let bars = "";

  monthly.forEach((month, i) => {
    const height = Math.round(
      ((CHART_BOTTOM - CHART_TOP) * month.count) /
      maxCount
    );

    const x =
      CHART_LEFT +
      i * slot +
      (slot - barWidth) / 2;

    const y = CHART_BOTTOM - height;
    const label = month.month.slice(5, 7);

    bars += `
      <rect
        class="bar"
        x="${x.toFixed(1)}"
        y="${y}"
        width="${barWidth.toFixed(1)}"
        height="${height}"
        fill="var(--ink)"
        style="transform-origin:${x.toFixed(1)}px ${CHART_BOTTOM}px"
      />

      <text
        x="${(x + barWidth / 2).toFixed(1)}"
        y="${CHART_BOTTOM + 16}"
        text-anchor="middle"
        fill="var(--dim)"
      >${label}</text>
    `;
  });

  return bars.trim();
}

// --------------------------------------------------
// Template renderer
// --------------------------------------------------

async function renderFromTemplate(
  templatePath,
  outputPath,
  replacements
) {
  let svg;

  try {
    svg = await fs.readFile(templatePath, "utf8");
  } catch (error) {
    if (error.code === "ENOENT") {
      throw new Error(
        `Template not found: ${path.relative(REPO_ROOT, templatePath)}\n` +
        `Repository root: ${REPO_ROOT}\n` +
        `Script directory: ${SCRIPT_DIR}\n` +
        "Check that the template is committed to the same branch and commit being built."
      );
    }

    throw error;
  }

  for (const [placeholder, value] of Object.entries(replacements)) {
    svg = svg.replaceAll(placeholder, value);
  }

  const dir = path.dirname(outputPath);

  await fs.mkdir(dir, { recursive: true });
  await fs.writeFile(outputPath, svg, "utf8");

  console.log(
    `Wrote ${path.relative(REPO_ROOT, outputPath)}`
  );
}

// --------------------------------------------------
// Main
// --------------------------------------------------

async function main() {
  console.log(`Working directory: ${process.cwd()}`);
  console.log(`Repository root: ${REPO_ROOT}`);
  console.log(`Script directory: ${SCRIPT_DIR}`);

  console.log(`Fetching repositories for ${USERNAME}...`);

  const repos = await getAllRepos();

  console.log(
    `Found ${repos.length} public, non-fork repositories.`
  );

  const languageTotals = {};
  let totalStars = 0;

  for (const repo of repos) {
    totalStars += repo.stargazers_count || 0;

    const languages =
      await getLanguagesForRepo(repo.name);

    for (const [lang, bytes] of Object.entries(languages)) {
      languageTotals[lang] =
        (languageTotals[lang] || 0) + bytes;
    }
  }

  const languages = toPercentages(languageTotals);

  console.log("Fetching GitHub stats via GraphQL...");

  const ghStats = await getGithubStats();

  const monthly =
    monthlyTotalsFromCalendar(ghStats.calendarDays);

  const stats = {
    generatedAt: new Date().toISOString(),
    repoCount: repos.length,
    totalStars,
    languages,
    totalCommits: ghStats.totalCommits,
    totalPRs: ghStats.totalPRs,
    totalIssues: ghStats.totalIssues,
    contributedTo: ghStats.contributedTo,
    monthlyContributions: monthly,
  };

  console.log(
    "Computed stats:",
    JSON.stringify(stats, null, 2)
  );

  // Save raw statistics.
  await fs.mkdir(repoPath("assets"), {
    recursive: true,
  });

  await fs.writeFile(
    repoPath("assets", "stats.json"),
    JSON.stringify(stats, null, 2),
    "utf8"
  );

  // ----------------------------------------------
  // 1. Telemetry panels
  // ----------------------------------------------

  const telemetryBars =
    buildLanguageRowsTelemetry(languages);

  for (const target of TELEMETRY_TARGETS) {
    await renderFromTemplate(
      target.template,
      target.output,
      {
        "<!-- LANGUAGE_ROWS -->": telemetryBars,
        "{{REPO_COUNT}}": String(stats.repoCount),
      }
    );
  }

  // ----------------------------------------------
  // 2. GitHub statistics panels
  // ----------------------------------------------

  const statsLangBars =
    buildLanguageBarsForStatsPanel(languages);

  for (const target of GITHUB_STATS_TARGETS) {
    await renderFromTemplate(
      target.template,
      target.output,
      {
        "{{TOTAL_STARS}}": String(stats.totalStars),
        "{{TOTAL_COMMITS}}": String(stats.totalCommits),
        "{{TOTAL_PRS}}": String(stats.totalPRs),
        "{{TOTAL_ISSUES}}": String(stats.totalIssues),
        "{{CONTRIBUTED_TO}}": String(stats.contributedTo),
        "<!-- LANGUAGE_BAR_ROWS -->": statsLangBars,
      }
    );
  }

  // ----------------------------------------------
  // 3. Contribution graph panels
  // ----------------------------------------------

  const contributionBars =
    buildContributionBars(monthly);

  for (const target of CONTRIBUTION_TARGETS) {
    await renderFromTemplate(
      target.template,
      target.output,
      {
        "<!-- CONTRIBUTION_BARS -->": contributionBars,
      }
    );
  }

  console.log("All GitHub statistics SVGs generated successfully!");
}

// --------------------------------------------------
// Error handling
// --------------------------------------------------

main().catch((error) => {
  console.error("Failed to generate GitHub statistics:");
  console.error(error);
  process.exit(1);
});

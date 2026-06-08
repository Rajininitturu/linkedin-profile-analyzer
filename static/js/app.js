const nameInput = document.getElementById("profile-name-input");
const headlineInput = document.getElementById("profile-headline-input");
const aboutInput = document.getElementById("profile-about-input");
const skillsInput = document.getElementById("profile-skills-input");
const analyzeBtn = document.getElementById("analyze-btn");
const errorMsg = document.getElementById("error-msg");
const resultsSection = document.getElementById("results");
const emailInput = document.getElementById("email-input");
const sendBtn = document.getElementById("send-btn");
const emailStatus = document.getElementById("email-status");

let currentReport = null;

const BREAKDOWN_LABELS = {
  headline: "Headline",
  about: "About",
  skills: "Skills",
  experience: "Experience",
};

function setLoading(btn, loading) {
  const text = btn.querySelector(".btn-text");
  const spinner = btn.querySelector(".spinner");
  btn.disabled = loading;
  text.classList.toggle("hidden", loading);
  spinner.classList.toggle("hidden", !loading);
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.remove("hidden");
}

function hideError() {
  errorMsg.classList.add("hidden");
}

function scoreColor(score) {
  if (score >= 75) return "#059669";
  if (score >= 50) return "#0a66c2";
  if (score >= 30) return "#d97706";
  return "#dc2626";
}

function animateScore(score) {
  const circle = document.getElementById("score-circle");
  const numberEl = document.getElementById("score-number");
  const circumference = 2 * Math.PI * 52;
  const offset = circumference - (score / 100) * circumference;

  circle.style.strokeDashoffset = offset;
  circle.style.stroke = scoreColor(score);

  let current = 0;
  const step = Math.max(1, Math.floor(score / 30));
  const interval = setInterval(() => {
    current = Math.min(current + step, score);
    numberEl.textContent = current;
    if (current >= score) clearInterval(interval);
  }, 30);
}

function renderBreakdown(breakdown) {
  const container = document.getElementById("breakdown");
  container.innerHTML = "";

  for (const [key, value] of Object.entries(breakdown)) {
    const pct = (value / 25) * 100;
    const item = document.createElement("div");
    item.className = "breakdown-item";
    item.innerHTML = `
      <span style="min-width:80px">${BREAKDOWN_LABELS[key]}</span>
      <div class="breakdown-bar"><div class="breakdown-fill" style="width:0%"></div></div>
      <span style="min-width:36px;text-align:right;font-weight:600">${value}/25</span>
    `;
    container.appendChild(item);
    requestAnimationFrame(() => {
      item.querySelector(".breakdown-fill").style.width = `${pct}%`;
    });
  }
}

function renderSkills(skills) {
  const container = document.getElementById("skills-list");
  document.getElementById("skills-count").textContent = skills.length;

  if (!skills.length) {
    container.innerHTML = '<p class="empty-state">No skills entered</p>';
    return;
  }
  container.innerHTML = skills
    .map((s) => `<span class="skill-tag">${escapeHtml(s)}</span>`)
    .join("");
}

function renderSuggestions(suggestions) {
  const list = document.getElementById("suggestions-list");
  list.innerHTML = suggestions.map((s) => `<li>${escapeHtml(s)}</li>`).join("");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function displayResults(data) {
  currentReport = data;
  const profile = data.profile;

  document.getElementById("profile-name").textContent = profile.name || "Unknown";
  document.getElementById("profile-headline").textContent = profile.headline || "No headline";
  document.getElementById("profile-about").textContent = profile.about || "No about section";

  animateScore(data.score);
  renderBreakdown(data.breakdown);
  renderSkills(profile.skills);
  renderSuggestions(data.suggestions);

  resultsSection.classList.remove("hidden");
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

analyzeBtn.addEventListener("click", async () => {
  const name = nameInput.value.trim();
  if (!name) {
    showError("Please enter your name.");
    nameInput.focus();
    return;
  }

  hideError();
  setLoading(analyzeBtn, true);

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        headline: headlineInput.value,
        about: aboutInput.value,
        skills: skillsInput.value,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Analysis failed");
    displayResults(data);
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(analyzeBtn, false);
  }
});

sendBtn.addEventListener("click", async () => {
  const email = emailInput.value.trim();
  if (!email) {
    emailStatus.textContent = "Please enter an email address.";
    emailStatus.className = "status-msg error";
    emailStatus.classList.remove("hidden");
    return;
  }
  if (!currentReport) {
    emailStatus.textContent = "Analyze a profile first.";
    emailStatus.className = "status-msg error";
    emailStatus.classList.remove("hidden");
    return;
  }

  setLoading(sendBtn, true);
  emailStatus.classList.add("hidden");

  try {
    const res = await fetch("/api/send-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, report: currentReport }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to send email");

    emailStatus.textContent = `Report sent successfully to ${email}!`;
    emailStatus.className = "status-msg success";
    emailStatus.classList.remove("hidden");
  } catch (err) {
    emailStatus.textContent = err.message;
    emailStatus.className = "status-msg error";
    emailStatus.classList.remove("hidden");
  } finally {
    setLoading(sendBtn, false);
  }
});

# Amazon OA: HackerRank Environment & Proctoring FAQ (2026)

> **Platform:** HackerRank Assessment Engine  
> **Total Time:** ~2.5 hours in one sitting  
> **Hardware Requirements:** Single monitor, Webcam, Stable Broadband  

---

## 1. Proctoring Rules & System Constraints

Amazon's HackerRank proctoring environment enforces strict security controls. Violations can lead to automatic session invalidation without manual review.

### Rule 1: Single Monitor Requirement (MANDATORY)
- **Constraint:** The assessment system actively checks for connected external displays.
- **Action Required:**
  - If using a desktop with multiple monitors: **physically disconnect** the second monitor cable from your GPU/Mac.
  - If using a laptop connected to an external monitor: close the laptop lid (clamshell mode) so only ONE display is active, or disconnect the external monitor and use the laptop display exclusively.
  - Do not attempt to use virtual desktops or display mirror trickery; HackerRank's WebGL / Screen API queries display geometry.

### Rule 2: Full-Screen Lock & Window Focus
- The coding assessment will prompt you to enter **Full Screen Mode**.
- **Do not switch tabs.** Tab switching, clicking out of the browser window, or pressing `Cmd+Tab` / `Alt+Tab` triggers focus-loss events.
- Disable all desktop notifications, Slack, Discord, and calendar pop-ups before launching the test. A background notification stealing window focus can register as a focus-loss flag.

### Rule 3: External Assistance & Tool Restrictions
- **No External IDEs:** You cannot copy code to VS Code, PyCharm, or local terminals. All coding and compiling must happen inside the in-browser IDE.
- **No External AI Tools:** Do NOT open ChatGPT, Claude, Cursor, or Copilot in another tab, device, or phone. Amazon and HackerRank log keystroke intervals, paste buffers, and syntax burst anomalies.
- **Allowed AI:** In **Question 2 ONLY**, you will have access to the **official embedded AI Assistant** inside the HackerRank interface. Use only this assistant.

---

## 2. In-Browser IDE Features & Compiler Settings

### Languages Supported:
- **Question 1 (DSA):** C, C++, C++14, C#, Go, Java 7/8, JavaScript (Node.js), Kotlin, Objective-C, PyPy, PyPy3, Python 2/3, Ruby, Scala, Swift.
  - *Recommendation:* Use **Python 3** (or Java 8/17 if Java-first). Python allows faster implementation of sliding windows, heaps, and graph traversals with clean syntax.
- **Question 2 (Code Repository):** Limited language subset depending on the repo stack provided (typically Python 3 or Java).
  - *CRITICAL:* **You cannot change your language once you begin Question 2.** Ensure your language selector is correct before confirming.

### Keyboard Shortcuts & IDE Settings:
- **Settings Gear Icon (top right of editor):** You can configure Tab Size (2 vs 4 spaces), Key Binding (Standard vs Vim/Emacs), and Dark Mode.
- **Auto-Complete & Linting:** Basic syntax highlighting and bracket matching are enabled, but deep IntelliSense may be limited compared to desktop IDEs.
- **Running Custom Test Cases:**
  - Always use the **"Test with custom input"** checkbox below the editor.
  - Paste your edge cases (e.g., `[]`, `[1]`, large inputs) to verify boundary conditions before submitting.

---

## 3. Pre-Flight Test Day Checklist

Complete this checklist 30 minutes before clicking the test link:

- [ ] **Restroom & Hydration:** Have water nearby; the timer cannot be paused once started.
- [ ] **Display Setup:** Verify only 1 physical monitor is detected in OS Display Settings.
- [ ] **Browser:** Update Google Chrome or Microsoft Edge to the latest version. Disable ad-blockers or aggressive extensions that might block WebSockets.
- [ ] **System Background Apps:** Force quit Slack, Zoom, Discord, Teams, WhatsApp, Spotify, and terminal windows.
- [ ] **Do Not Disturb Mode:** Turn on Mac/Windows "Do Not Disturb" to suppress all banners.
- [ ] **Government ID:** Keep your driver's license or passport on your desk in case of photo verification.
- [ ] **Test Link Verification:** Open the HackerRank Demo Link first to get used to the interface before touching your live assessment link.

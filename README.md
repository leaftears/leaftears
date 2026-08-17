<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,60:1f3d68,100:2F81F7&height=190&section=header&text=Mika&fontSize=68&fontColor=ffffff&fontAlignY=34&desc=local-first%20desktop%20software&descAlignY=56&descSize=17" alt="Mika" />
</p>

<p align="center">
  <a href="https://github.com/mika2go?tab=repositories">
    <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=500&size=21&pause=1200&color=2F81F7&center=true&vCenter=true&width=600&height=42&lines=Native+desktop+tools+that+stay+out+of+the+way;Linux+and+Windows+internals;Small+footprints+and+honest+status" alt="Native desktop tools, Linux and Windows internals, small footprints" />
  </a>
</p>

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=mika2go&label=Profile+Views&color=2F81F7&style=flat-square" alt="Profile views" />
  <img src="https://img.shields.io/badge/Rust-000000?style=flat-square&logo=rust&logoColor=white" alt="Rust" />
  <img src="https://img.shields.io/badge/Linux-0d1117?style=flat-square&logo=linux&logoColor=FCC624" alt="Linux" />
  <img src="https://img.shields.io/badge/Wayland-0d1117?style=flat-square&logo=wayland&logoColor=white" alt="Wayland" />
  <img src="https://img.shields.io/badge/License-MIT-2F81F7?style=flat-square" alt="MIT licensed projects" />
</p>

## Focus

- **Systems programming in Rust and C++, on Windows and Linux.** GPU frame
  capture, hardware video encoding, real-time audio pipelines, and the bounded
  in-memory ring buffers that let a recorder hold the last minute without
  touching the disk.
- **Native interfaces, no web stack.** Direct2D and DirectWrite on Windows,
  Qt Quick and QML, GTK4 on Linux, Ratatui in the terminal — picked so an idle
  application costs tens of megabytes instead of hundreds.
- **Platform APIs where the edges are sharp.** Windows Graphics Capture, D3D11,
  Media Foundation and WASAPI; Wayland and Hyprland, PipeWire, systemd user
  services, and Arch packaging on the other side.
- **Local-first by construction, not by policy.** No accounts, no telemetry, no
  upload path — the Linux recorder ships with network access denied in its unit
  file rather than merely unused.
- **Measured instead of asserted.** Memory and bitrate budgets are explicit and
  enforced, footprints are compared against real alternatives with the raw
  numbers published, and releases are validated end to end in a disposable
  Windows 11 VM.
- **Boring release discipline.** Locked workspaces, `clippy -D warnings` as a
  gate, native CI that builds and exercises the installer, and SHA-256 build
  evidence attached to every release.

## Featured Projects

<table>
  <tr>
    <td width="50%" valign="top">
      <a href="https://github.com/mika2go/PIDRA">
        <img width="100%" src="https://socialify.git.ci/mika2go/PIDRA/image?description=0&font=Inter&forks=0&issues=0&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2Fmika2go%2FMika2Go%2Fmain%2Fassets%2Flogo-pidra.png&name=1&owner=1&pattern=Circuit+Board&pulls=0&stargazers=0&theme=Dark" alt="Pidra" />
      </a>
      <p>Which desktop application is eating your memory, and what actually happened after you tried to stop it. GUI applications instead of every process on the machine, whole process trees totalled rather than a browser's root, and close-risk notes before you kill something.</p>
      <p><code>Rust</code> <code>Ratatui</code> <code>Linux</code> <code>TUI</code></p>
    </td>
    <td width="50%" valign="top">
      <a href="https://github.com/mika2go/Trellis">
        <img width="100%" src="https://socialify.git.ci/mika2go/Trellis/image?description=0&font=Inter&forks=0&issues=0&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2Fmika2go%2FMika2Go%2Fmain%2Fassets%2Flogo-trellis.png&name=1&owner=1&pattern=Circuit+Board&pulls=0&stargazers=0&theme=Dark" alt="Trellis" />
      </a>
      <p>A local-first ledger for your repositories: Git state, branches, recent commits and detected build systems, on the desktop and without an account or a network connection. Optional GitHub authorization is in progress.</p>
      <p><code>Rust</code> <code>GTK4</code> <code>Git</code> <code>Local-first</code></p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="https://github.com/mika2go/Wreath">
        <img width="100%" src="https://socialify.git.ci/mika2go/Wreath/image?description=0&font=Inter&forks=0&issues=0&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2Fmika2go%2FMika2Go%2Fmain%2Fassets%2Flogo-wreath.png&name=1&owner=1&pattern=Circuit+Board&pulls=0&stargazers=0&theme=Dark" alt="Wreath" />
      </a>
      <p>The last half minute of gameplay, hardware-encoded in memory and written out only when you press the shortcut. Native on Windows, a small service plus GTK4 library on Linux, and nothing ever leaves the machine.</p>
      <p><code>Rust</code> <code>Direct2D</code> <code>Media Foundation</code> <code>WASAPI</code> <code>GTK4</code></p>
      <p>
        <img src="https://img.shields.io/github/v/release/mika2go/Wreath?style=flat-square&color=2F81F7&label=release" alt="Latest Wreath release" />
        <img src="https://img.shields.io/badge/Windows%20%2B%20Linux-0d1117?style=flat-square" alt="Windows and Linux" />
      </p>
    </td>
    <td width="50%" valign="top">
      <a href="https://github.com/mika2go/dotfiles">
        <img width="100%" src="https://socialify.git.ci/mika2go/dotfiles/image?description=0&font=Inter&forks=0&issues=0&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2Fmika2go%2FMika2Go%2Fmain%2Fassets%2Flogo-dotfiles.png&name=1&owner=1&pattern=Circuit+Board&pulls=0&stargazers=0&theme=Dark" alt="Hyprland and Quickshell dotfiles" />
      </a>
      <p>My Arch desktop: a QML shell with a vertical bar, Dynamic Island, launcher, dashboard, notifications, wallpaper tools, a lock screen and a cautious installer.</p>
      <p><code>QML</code> <code>Quickshell</code> <code>Hyprland</code> <code>Arch Linux</code> <code>Wayland</code></p>
    </td>
  </tr>
</table>

## Open Source Contributions

<table>
  <tr>
    <td width="50%" valign="top">
      <a href="https://github.com/mika2go/eddy">
        <img width="100%" src="https://socialify.git.ci/mika2go/eddy/image?description=0&font=Inter&forks=0&issues=0&language=1&name=1&owner=1&pattern=Circuit+Board&pulls=0&stargazers=0&theme=Dark" alt="Eddy" />
      </a>
      <p>I contributed the Windows version only: native platform integration and the Windows installer packaging.</p>
      <p><code>Windows</code> <code>C++</code> <code>Qt</code> <code>CMake</code> <code>MSI</code> <code>NSIS</code></p>
    </td>
    <td width="50%" valign="top">
      <a href="https://github.com/mika2go/boltsnap">
        <img width="100%" src="https://socialify.git.ci/mika2go/boltsnap/image?description=0&font=Inter&forks=0&issues=0&language=1&name=1&owner=1&pattern=Circuit+Board&pulls=0&stargazers=0&theme=Dark" alt="BoltSnap" />
      </a>
      <p>I contributed the Windows version only of this fast screenshot and annotation workflow.</p>
      <p><code>Windows</code> <code>Rust</code> <code>Screen Capture</code></p>
    </td>
  </tr>
</table>

## Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=rust,cpp,qt,cs,dotnet,python,fastapi,ts,react,tailwind,nodejs,tauri,supabase,linux&perline=14" alt="Rust, C++, Qt, C sharp, .NET, Python, FastAPI, TypeScript, React, Tailwind CSS, Node.js, Tauri, Supabase, Linux" />
</p>

## GitHub in Numbers

<p align="center">
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=mika2go&theme=github_dark" alt="Profile summary" />
</p>

<p align="center">
  <img height="200" src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=mika2go&theme=github_dark" alt="Repositories per language" />
  <img height="200" src="https://github-profile-summary-cards.vercel.app/api/cards/most-commit-language?username=mika2go&theme=github_dark" alt="Most committed languages" />
</p>

<p align="center">
  <img src="./assets/stats.svg" alt="Contribution activity over the last year, private repositories included" width="760" />
</p>

<p align="center">
  <sub>Rebuilt daily by <a href="scripts/build-stats.py">scripts/build-stats.py</a> — the hosted streak cards
  query GitHub with their own token and therefore only ever see public repositories.</sub>
</p>

<p align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=mika2go&days=31&bg_color=00000000&color=C9D1D9&line=2F81F7&point=2F81F7&area_color=2F81F7&area=true&hide_border=true&hide_title=false&custom_title=Commits%20over%20the%20last%2031%20days" alt="Commit activity over the last 31 days" />
</p>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:2F81F7,40:1f3d68,100:0d1117&height=120&section=footer&text=useful%20software%20%C2%B7%20quiet%20interfaces&fontSize=20&fontColor=ffffff&fontAlignY=72" alt="Useful software, quiet interfaces" />
</p>
# Step 3: Push Your Code to GitHub

Your code needs to be hosted on GitHub so that:
- **GitHub Actions** can automatically build and deploy your backend whenever you push changes
- **Vercel** can automatically deploy your frontend whenever you push changes

This guide walks you through creating a GitHub repository and pushing your existing code to it.

---

## 3.1 Create a New Repository on GitHub

1. Open your browser and go to [github.com](https://github.com)
2. Sign in to your account (or create one if you don't have one)
3. In the top-right corner, click the **+** button (plus icon)
4. Click **"New repository"**
5. Fill in the form:
   - **Repository name**: Choose a name (e.g., `multi-agent-platform` or `Mulit_agents_for_production`)
   - **Description** (optional): "Multi-agent AI platform with PO Parser and Image Tagging"
   - **Visibility**: Choose **Public** (free GitHub Actions minutes, free container registry) or **Private** (2,000 free CI/CD minutes/month)
   - **DO NOT** check "Add a README file" -- you already have one
   - **DO NOT** check "Add .gitignore" -- you already have one
   - **DO NOT** choose a license for now
6. Click **"Create repository"**
7. You'll see a page with setup instructions -- leave this page open, you'll need the URL

---

## 3.2 Verify .env Is Not Tracked by Git

Before pushing anything, make sure your `.env` file (which contains API keys) will NOT be uploaded to GitHub.

Open PowerShell, navigate to your project:

```powershell
cd "c:\Nagdy\Mustafa\MIS\Real Projects\Mulit_agents_for_production"
```

Check that `.env` is in your `.gitignore`:

```powershell
Select-String -Path ".gitignore" -Pattern "^\.env$"
```

You should see a match like `.gitignore:1:.env`. This means Git will ignore the `.env` file and it will NOT be pushed to GitHub. Your API keys are safe.

If you do NOT see a match, add it manually:

```powershell
Add-Content -Path ".gitignore" -Value "`n.env"
```

---

## 3.3 Initialize Git (if not already done)

Check if Git is already initialized:

```powershell
git status
```

**If you see `fatal: not a git repository`**, initialize it:

```powershell
git init
```

**If you see a list of files** (tracked/untracked), Git is already initialized -- skip to the next section.

---

## 3.4 Stage and Commit Your Code

Add all files to Git's staging area:

```powershell
git add .
```

Verify that `.env` is NOT in the staged files:

```powershell
git status
```

Look through the list of files under "Changes to be committed". You should see your source code files but you should **NOT** see `.env`. If you see `.env` listed, stop and run:

```powershell
git rm --cached .env
```

Now create your first commit:

```powershell
git commit -m "Initial commit: Multi-Agent Platform with PO Parser and Image Tagging agents"
```

---

## 3.5 Make Sure Your Branch Is Named "main"

GitHub expects the default branch to be called `main`. Check your current branch name:

```powershell
git branch
```

If it shows `* master` instead of `* main`, rename it:

```powershell
git branch -M main
```

---

## 3.6 Connect to GitHub and Push

Go back to the GitHub page you left open in step 3.1. Find the URL that looks like:

```
https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

In PowerShell, add this as your remote:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repository name.

Now push your code:

```powershell
git push -u origin main
```

**What happens:**
- Git asks for your GitHub credentials. If you have two-factor authentication (2FA) enabled, you'll need to use a Personal Access Token instead of your password.
- All your code uploads to GitHub.

### If you get an authentication error

GitHub no longer accepts passwords for Git operations. You need a Personal Access Token (PAT):

1. Go to GitHub > Click your profile picture (top-right) > **Settings**
2. Scroll down the left sidebar > Click **"Developer settings"** (at the very bottom)
3. Click **"Personal access tokens"** > **"Tokens (classic)"**
4. Click **"Generate new token"** > **"Generate new token (classic)"**
5. Give it a name like "Git push access"
6. Set expiration to 90 days (or longer)
7. Check the **"repo"** scope (this gives full access to your repositories)
8. Click **"Generate token"**
9. **Copy the token immediately** (you can't see it again!)
10. When Git asks for your password, paste this token instead of your actual password

---

## 3.7 Verify on GitHub

1. Go to your repository page on GitHub (e.g., `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`)
2. Refresh the page
3. You should see all your project files listed
4. Click on a few files to make sure the code is there
5. **Verify that `.env` is NOT listed** -- this is critical for security

---

## Common Errors

| Error | Fix |
|---|---|
| `remote origin already exists` | You already added a remote. Remove it first: `git remote remove origin`, then try adding it again. |
| `failed to push some refs` | Someone else might have initialized the repo with a README. Run `git pull origin main --rebase` first, then push again. |
| `Permission denied` | Check that your GitHub username is correct and you have write access to the repo. Use a Personal Access Token for authentication. |
| `fatal: not a git repository` | You're not in the right directory. Run `cd "c:\Nagdy\Mustafa\MIS\Real Projects\Mulit_agents_for_production"` first. |

---

## Next Step

Once your code is on GitHub and you've verified `.env` is not visible, proceed to:
--> [04-setup-github-secrets.md](04-setup-github-secrets.md) (Configure GitHub Secrets)

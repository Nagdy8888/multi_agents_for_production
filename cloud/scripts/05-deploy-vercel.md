# Step 5: Deploy Frontend to Vercel

Vercel is a cloud platform built specifically for frontend frameworks like Next.js. It offers a free Hobby plan with unlimited deployments. Once connected to your GitHub repository, Vercel automatically rebuilds and redeploys your frontend every time you push code -- no commands needed.

---

## 5.1 Create a Vercel Account

1. Open your browser and go to [vercel.com](https://vercel.com)
2. Click **"Sign Up"** (top-right corner)
3. Click **"Continue with GitHub"** -- this connects Vercel to your GitHub account
4. GitHub will ask you to authorize Vercel -- click **"Authorize Vercel"**
5. You'll be redirected to the Vercel dashboard

By signing up with GitHub, Vercel can automatically access your repositories for deployment.

---

## 5.2 Import Your Repository

1. On the Vercel dashboard, click **"Add New..."** (top-right)
2. Click **"Project"**
3. You'll see a list of your GitHub repositories
4. Find your repository (e.g., `multi-agent-platform`) and click **"Import"**

If you don't see your repository:
- Click **"Adjust GitHub App Permissions"** at the bottom of the repository list
- This opens GitHub settings -- select your repository and click **"Save"**
- Go back to Vercel and refresh the page

---

## 5.3 Configure the Project

After importing, Vercel shows a configuration page. Set these options:

### Framework Preset

Vercel should auto-detect **Next.js**. If it shows something else, click the dropdown and select **Next.js**.

### Root Directory

This is the most important setting. Your frontend code is NOT in the root of the repo -- it's in `apps/frontend`.

1. Find the **"Root Directory"** field
2. Click **"Edit"** (or the pencil/browse icon next to it)
3. Type `apps/frontend` in the text field
4. Click **"Continue"** or press Enter

If you skip this step, the build will fail because Vercel will look for `package.json` in the repo root (where it doesn't exist for the frontend).

### Build and Output Settings

Leave these as the defaults. Vercel knows how to build Next.js apps automatically:
- Build Command: `next build` (auto-detected)
- Output Directory: `.next` (auto-detected)
- Install Command: `npm install` (auto-detected)

### Environment Variables

You need to tell your frontend where the backend API is running. Click **"Environment Variables"** to expand the section, then add:

1. Click **"Add"** (or the **+** button)
2. **Name**: `NEXT_PUBLIC_API_URL`
3. **Value**: Your Azure App Service URL from Step 2 (e.g., `https://multiagent-app.azurewebsites.net`)
4. Make sure all three environments are checked: **Production**, **Preview**, and **Development**
5. Click **"Add"** to save the variable

Where to find your backend URL:
- It was printed at the end of the `02-setup-azure.ps1` script
- The format is `https://YOUR_APP_NAME.azurewebsites.net`
- Or run this in PowerShell: `az webapp show --name multiagent-app --resource-group multiagent-rg --query "defaultHostName" --output tsv`

---

## 5.4 Deploy

1. Click the **"Deploy"** button
2. Vercel starts building your project -- you can watch the build logs in real-time
3. The build takes about 1-3 minutes
4. When it finishes, you'll see a **"Congratulations!"** screen with a preview of your deployed site

Your frontend is now live at a URL like: `https://your-project-name.vercel.app`

Click the URL or the preview image to open your live site in a new tab.

---

## 5.5 Verify Everything Works

1. Open your Vercel URL in the browser
2. The frontend should load and display the image tagging dashboard
3. Try uploading an image or performing an action that calls the backend
4. If the frontend loads but API calls fail, check:
   - Is the `NEXT_PUBLIC_API_URL` set correctly? (no trailing slash)
   - Is your Azure App Service running? Open the backend URL directly to verify
   - Does your Azure App Service have CORS configured to allow requests from your Vercel domain?

### CORS Note

Your FastAPI backend may need to allow requests from your Vercel domain. If you see CORS errors in the browser console, you'll need to update the CORS middleware in `apps/agents/src/api/main.py` to include your Vercel URL in the allowed origins list.

---

## Future Deployments

After the initial setup, everything is automatic:

- **Push to `main` branch** --> Vercel detects the change and rebuilds the frontend
- **Push frontend code** (`apps/frontend/`) --> New version deployed in ~1-2 minutes
- **Push backend code** (`apps/agents/`) --> GitHub Actions deploys to Azure (separate pipeline)

You don't need to visit Vercel or run any commands. Just `git push` and both backend and frontend update automatically.

---

## Updating the Backend URL Later

If your Azure App Service URL changes (e.g., you recreated the resources):

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click on your project name
3. Click the **"Settings"** tab (top navigation)
4. In the left sidebar, click **"Environment Variables"**
5. Find `NEXT_PUBLIC_API_URL` and click the three-dot menu (or edit icon) on the right
6. Click **"Edit"**
7. Update the value to your new Azure URL
8. Click **"Save"**
9. Go to the **"Deployments"** tab
10. Click the three-dot menu on the latest deployment
11. Click **"Redeploy"** to apply the new environment variable

---

## Common Errors

| Error | Fix |
|---|---|
| Build fails with "Cannot find module" | Make sure Root Directory is set to `apps/frontend` in Project Settings |
| `NEXT_PUBLIC_API_URL` is undefined | Add the environment variable in Vercel Settings > Environment Variables. Make sure all three environments (Production, Preview, Development) are checked. Then redeploy. |
| CORS error in browser console | Add your Vercel URL to the allowed origins in `apps/agents/src/api/main.py` CORS middleware, commit, and push to trigger a backend redeployment. |
| "This project's root directory does not contain a `package.json` file" | The Root Directory is wrong. Go to Project Settings > General > Root Directory and change it to `apps/frontend`. |
| Build succeeds but page is blank | Check the browser developer console (F12) for errors. Usually a missing or incorrect `NEXT_PUBLIC_API_URL`. |

---

## You're Done!

Congratulations -- your full-stack application is now deployed:

- **Backend**: `https://multiagent-app.azurewebsites.net` (Azure App Service)
- **Frontend**: `https://your-project.vercel.app` (Vercel)
- **CI/CD**: Automatic on every `git push` to `main`

Both services are on free tiers and will cost you $0/month within the free allowances.

To tear everything down later, see the Tear Down section in the [main README](../README.md).

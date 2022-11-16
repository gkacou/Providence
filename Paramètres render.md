**=== Environment variables excluded from render.yaml**
The following environment variables were not included in the generated
  render.yaml file because they potentially contain secrets. You may need to
  manually add them to your service in the Render Dashboard.

- DATABASE_URL: postgres://brisapafiuttga:cf8b56e4012d5bda7799149d84398d47af111c6720ba2b74be877d7e3e88639e@ec2-52-211-37-76.eu-west-1.compute.amazonaws.com:5432/ddou0djinscv26
- SECRET_KEY: 4@f_b+a$&hxefe6irnl@&&*ud(+-v8*23#fw)ws7(c7=!0o#w#

**=== Follow these steps to complete import of service(s) and database(s) to Render**
1. Add, commit, and push the generated .render-buildpacks.json, render.yaml and Dockerfile.render to GitHub or GitLab.
2. Go to https://dashboard.render.com/select-repo?type=blueprint
3. Search for and select this repository.
4. Verify the plan showing the resources that Render will create, and
   then click 'Create New Resources'.
5. After the resources are deployed, you may need to manually add
   the above environment variables to your Web Service in the Render Dashboard.
   They were not included in the generated render.yaml because they potentially
   contain secrets.

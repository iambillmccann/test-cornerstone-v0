This document contains references to Cornerstone

I'm not happy with the "pull" style of deployment. It doesn't fit the use case for a template app. With this deploy, the services must always be deployed and watching for changes. But I don't want a version of Cornerstone out in the cloud doing nothing. It's just a template after all. The only reason to deploy it is for end-to-end acceptance testing. Otherwise the services should be shut down. So I will probably want to change the deployment workflow. And have a teardown workflow too.

I'm also not thrilled with the Clerk UI. As a service, it's great. But I don't want those Clerk branded popups. So I will need to add registration and login forms, and settings with account management.

# ChatGPT Work adapter

ChatGPT Work can use Project instructions and uploaded sources, but it does not automatically have direct access to a folder on your phone or computer. This adapter exports the repository as an explicitly labelled snapshot.

## Use a project pack

Open exports/chatgpt-work/<project-id>/ for the project you need.

1. Create or open a ChatGPT Project.
2. Copy the contents of PROJECT-INSTRUCTIONS.md into the Project instructions field.
3. Upload the Lattice_ChatGPT_Work_Pack_<project-id>.md file as a Project source.
4. Start a Work chat in that Project and use Activate Lattice or Resume Lattice.
5. After a substantive delivery, copy exact returned file updates back into the repository and regenerate the pack.

## Regenerate after repository changes

    python3 scripts/lattice.py export-chatgpt-work --project <project-id> --overwrite

The pack retains source headings for the Agency Kernel, Portfolio Registry, and one Project Capsule. It is a snapshot, never a second source of truth.

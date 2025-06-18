import os
import re
import subprocess
import typer
from pathlib import Path

app = typer.Typer()


def run_command(command: str):
    """Run a shell command and handle errors."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        typer.echo(f"Error running command: {command}\n{result.stderr}", err=True)
        raise typer.Exit(code=result.returncode)
    else:
        typer.echo(result.stdout)
        typer.echo(f"Command succeeded: {command}")


def remove_type_hints(line):
    if "\":" in line:
        return line

    return re.sub(r'(\s*:\s*["\w\[\], ]+)', '', line)

def remove_classmethod_methods(code):
    """
    Removes methods decorated with @classmethod from the given code.

    Args:
        code (str): The code from which to remove @classmethod methods.

    Returns:
        str: The code with @classmethod methods removed.
    """
    lines = code.split('\n')
    new_lines = []
    skip = False
    skip_indent = None
    i = 0

    while i < len(lines):
        line = lines[i]

        if not skip:
            if re.match(r'^\s*@classmethod\s*$', line.strip()):
                # Start skipping from the decorator line
                skip = True
                # Next line should be the 'def' line; get its indentation
                i += 1
                if i < len(lines):
                    def_line = lines[i]
                    match = re.match(r'^(\s*)def\s+', def_line)
                    if match:
                        skip_indent = len(match.group(1))
                    else:
                        # Not a method definition; add the current line back
                        skip = False
                        new_lines.append(line)
                        i -= 1  # Step back to re-process this line
                else:
                    break  # End of file
            else:
                new_lines.append(line)
        else:
            # Skip lines until indentation is less than or equal to skip_indent
            match = re.match(r'^(\s*)', line)
            current_indent = len(match.group(1))
            if line.strip() == '':
                # Empty line; continue skipping
                pass
            elif current_indent <= skip_indent:
                # Indentation is less or equal; stop skipping
                skip = False
                new_lines.append(line)
            else:
                # Continue skipping
                pass
        i += 1

    return '\n'.join(new_lines)

@app.command()
def create_migration(commit_msg: str, autogenerate: bool = typer.Option(False, help="Auto generate migration script")):
    """Create a new migration script."""
    line_to_remove = ["from python.server.database import __ENGINE"]
    source_dir = Path("python/model/database")
    header_file = Path("tools/migration/model_header.py")
    dest_file = Path("tools/migration/model.py")

    try:
        
        # Get all .py files in the directory and sort them alphabetically
        all_files = sorted([f for f in os.listdir(source_dir) if f.endswith(".py") and not f.startswith("_")])

        # Ensure that base.py is processed first
        if 'base.py' in all_files:
            all_files.remove('base.py')
            all_files.insert(0, 'base.py')
        
        with header_file.open('r') as f_header:
            header_lines = f_header.readlines()

        for filename in all_files:
            if filename.endswith(".py"):
                file_path = os.path.join(source_dir, filename)
                with open(file_path, 'r') as infile:
                    code = infile.read()
                    # Remove @classmethod methods from the code
                    code_without_classmethods = remove_classmethod_methods(code)
                    # Now process the code line by line
                    for line in code_without_classmethods.split('\n'):
                        # Exclude import statements
                        if not re.match(r'^\s*(import\s+|from\s+.*import\s+)', line):
                            # Remove type hints and add to header_lines
                            processed_line = remove_type_hints(line)
                            header_lines.append(processed_line + '\n')

        with dest_file.open('w+') as f_dest:
            f_dest.writelines(header_lines)

        typer.echo("File copied with line removed successfully!")
    except IOError as e:
        typer.echo(f"Unable to copy file with line removed. {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(code=1)

    command = f'alembic revision --autogenerate -m "{commit_msg}"' if autogenerate else f'alembic revision -m "{commit_msg}"'
    run_command(command)


@app.command()
def run_migration():
    """Run the migration to upgrade the database."""
    run_command("alembic upgrade head")


@app.command()
def migrate(commit_msg: str, autogenerate: bool = typer.Option(False, help="Auto generate migration script")):
    """Create and run a migration script."""
    create_migration(commit_msg, autogenerate)
    run_migration()


if __name__ == "__main__":
    app()

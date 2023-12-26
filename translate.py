import argparse
import asyncio
from dataclasses import dataclass
from io import StringIO
import re
import sys
from typing import IO, List
from openai import AsyncOpenAI


def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


@dataclass
class Entry:
    title: str
    content: str

    def section(self) -> str:
        """All titles are of the form '[Authors, Month Day, Year].
        I am extracting the section from each title as 'Month Year'"""
        matching = re.match(r"^\[.+,\s*(\w+)\s*\d+,\s*(\d+)\]", self.title)
        if matching:
            return f"{matching.group(1)} {matching.group(2)}"
        return self.title.strip("[]")


def load_journal(file_content: IO) -> List[Entry]:
    """The file format is pretty simple (See test_load_journal for an example).
    It is a list of entries, each with a title that contains the date and the author.
    I only care about the titles and the content for each entries."""
    lines = [l.strip() for l in file_content.readlines()]
    journal = []

    entry_title = ""
    entry_content = []

    entry_title_regex = r"^\[.*\]$"  # match "[Something]"
    for line in lines:
        if re.match(entry_title_regex, line):
            if entry_content:
                journal.append(Entry(entry_title, " ".join(entry_content)))
            entry_title = line
            entry_content = []
        else:
            if len(line) == 0:
                entry_content.append("\n\n")
            else:
                entry_content.append(line)

    if entry_content:
        journal.append(Entry(entry_title, " ".join(entry_content)))

    log(f"Loaded {len(journal)} entries")
    return journal


async def translate(entry: Entry, client: AsyncOpenAI, sem: asyncio.Semaphore) -> Entry:
    async with sem:
        log("Translating", entry.title)
        output = await client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": "Please translate every message from english into french."
                    "add comments about the translation between brackets if needed to improve the understanding."
                    "Do not write anything apart from the translation and the comments",
                },
                {"role": "user", "content": entry.content},
            ],
        )
        return Entry(entry.title, output.choices[0].message.content or "")


async def main(journal: List[Entry], parallel: int) -> None:
    client = AsyncOpenAI()
    sem = asyncio.Semaphore(parallel)

    log(f"{len(journal)} entries found in the journal")

    translations = [translate(entry, client, sem) for entry in journal]

    log("Translations queued")

    last_section = ""
    for entry in await asyncio.gather(*translations):
        if entry.section() != last_section:
            print(f"# {entry.section()}\n")
            last_section = entry.section()

        print(f"## {entry.title.strip('[]')}")
        print(f"{entry.content}\n\n")


def test_entry():
    e = Entry("[Clark, May 19, 1804]", "")
    assert e.section() == "May 1804"

    e = Entry("[Clark, August 22, 1805]", "")
    assert e.section() == "August 1805"

    e = Entry("[Ordway, May 17, 1804]", "")
    assert e.section() == "May 1804"

    e = Entry("[Lewis and Clark, June 24, 1804]", "")
    assert e.section() == "June 1804"

    e = Entry("[Transcriber's Note]", "")
    assert e.section() == "Transcriber's Note"


def test_load_journal():
    content = StringIO(
        """[Clark, October 12, 1805]
first
line

second line


[Clark, May 13, 1805]
next line
another one

"""
    )
    entries = load_journal(content)
    assert len(entries) == 2
    assert entries[0].title == "[Clark, October 12, 1805]"
    assert entries[0].content == "first line \n\n second line \n\n \n\n"

    assert entries[1].title == "[Clark, May 13, 1805]"
    assert entries[1].content == "next line another one"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=argparse.FileType("r", encoding="utf-8-sig"))
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--number", type=int, default=2)
    parser.add_argument("--parallel", type=int, default=5)
    args = parser.parse_args()

    journal = load_journal(args.file)[args.start : args.start + args.number]

    asyncio.run(main(journal, args.parallel))

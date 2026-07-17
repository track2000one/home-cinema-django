import re

from django import forms


EPISODE_CODE_RE = re.compile(r"^S(?P<season>\d+)E(?P<episode>\d+)$", re.IGNORECASE)


class BulkEpisodeImportForm(forms.Form):
    default_season_number = forms.IntegerField(
        label="Default season number",
        min_value=1,
        initial=1,
        help_text="Used when a line does not contain an SxxExx episode code.",
    )
    start_episode_number = forms.IntegerField(
        label="Starting episode number",
        min_value=1,
        initial=1,
        help_text="Used for URL-only lines or title | URL lines.",
    )
    episode_links = forms.CharField(
        label="Episode links",
        widget=forms.Textarea(
            attrs={
                "rows": 18,
                "placeholder": (
                    "Supported formats:\n\n"
                    "https://drive.google.com/file/d/FILE_ID/view\n\n"
                    "Episode title | https://drive.google.com/file/d/FILE_ID/view\n\n"
                    "S01E01 | Episode title | https://drive.google.com/file/d/FILE_ID/view"
                ),
            }
        ),
        help_text="Paste one episode per line. Seasons are created automatically.",
    )

    def parse_lines(self):
        cleaned = self.cleaned_data
        default_season = cleaned["default_season_number"]
        next_episode = cleaned["start_episode_number"]
        parsed = []
        errors = []

        for line_number, raw_line in enumerate(cleaned["episode_links"].splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            parts = [part.strip() for part in line.split("|")]
            season_number = default_season
            episode_number = next_episode
            title = ""
            url = ""

            if len(parts) == 1:
                url = parts[0]
                next_episode += 1
            elif len(parts) == 2:
                title, url = parts
                next_episode += 1
            elif len(parts) >= 3:
                code, title, url = parts[0], parts[1], parts[2]
                match = EPISODE_CODE_RE.match(code)
                if not match:
                    errors.append(f"Line {line_number}: invalid code '{code}'. Use S01E01.")
                    continue
                season_number = int(match.group("season"))
                episode_number = int(match.group("episode"))

            if not (url.startswith("https://") or url.startswith("http://")):
                errors.append(f"Line {line_number}: invalid URL.")
                continue

            parsed.append({
                "season_number": season_number,
                "episode_number": episode_number,
                "title": title,
                "url": url,
            })

        if errors:
            raise forms.ValidationError(errors)
        return parsed

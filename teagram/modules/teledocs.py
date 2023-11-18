from .. import loader, utils

from requests import get
from difflib import SequenceMatcher

def find_similar(input_string, string_list, threshold=0.3):
    similar_strings = []
    for string in string_list:
        similarity_ratio = SequenceMatcher(None, input_string, string).ratio()
        if similarity_ratio >= threshold:
            similar_strings.append((string, similarity_ratio))

    return similar_strings

@loader.module('Teledocs', 'itzlayz', 1.0)
class TeledocsMod(loader.Module):
    def get_text(self, request: str) -> int:
        similar = find_similar(request, self._json['requests'])
        request = max(similar, key=lambda x: x[1])[0] if similar else "Not found"
        if request == "Not found":
            return "❌ <b>Not found</b>"

        index = self._json['requests'].index(request)
        
        return (
            f"⚙ <b>{self._json['requests'][index]}</b>\n" + 
            (
                f"❔ <i>{self._json['requests_desc'][index][1]}</i>\n\n" 
                if self._json['requests_desc'][index][1] else "\n"
            ) +
            f'📜 <b>Example</b>:\n<pre language="py">{self._json["requests_ex"][index]}\n</pre>'
        )
    
    async def on_load(self):
        self._json = (await utils.run_sync(
            get,
            "https://raw.githubusercontent.com/itzlayz/teagram-assets/main/requests.json"
        )).json()
    
    @loader.command()
    async def tlcmd(self, message, args):
        await utils.answer(
            message,
            self.get_text(args.split(maxsplit=1)[0])
        )
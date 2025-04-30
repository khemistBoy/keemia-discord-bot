import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


class ChemicalElement:
    def __init__(self, element, number, symbol, weight, boil, melt, density, vapour, fusion):
        self.element = element
        self.number = number
        self.symbol = symbol
        self.weight = weight
        self.boil = boil
        self.melt = melt
        self.density = density
        self.vapour = vapour
        self.fusion = fusion

    def __str__(self):
        return (f"Element: {self.element}\n"
                f"Number: {self.number}\n"
                f"Symbol: {self.symbol}\n"
                f"Weight: {self.weight}\n"
                f"Boil: {self.boil}\n"
                f"Melt: {self.melt}\n"
                f"Density: {self.density}\n"
                f"vapour: {self.vapour}\n"
                f"Fusion: {self.fusion}")

class ChemicalElementService:
    def __init__(self, chemical_equation):
        self.chemical_equation = chemical_equation
        self.elements_dict = self.load_elements()

    def load_elements(self):
        elements_dict = {}
        with open("elements.csv", "r", encoding="utf-8") as f:
            data = [line.strip(",\n").split(",") for line in f.readlines()[1:]]
        fields = ["element", "number", "symbol", "weight", "boil", "melt", "density", "vapour", "fusion"]
        for row in data:
            while len(row) < len(fields):
                row.append("NaN")
            elements_data = dict(zip(fields, row))
            element_name = elements_data.pop("element")
            elements_dict[element_name] = elements_data
        return elements_dict

    def find_mass_by_symbol(self, symbol):
        for data in self.elements_dict.values():
            if data["symbol"] == symbol:
                return float(data["weight"])
        return None

    def calculate_mass(self):
        total_mass = 0.0
        i = 0
        while i < len(self.chemical_equation):
            symbol = self.chemical_equation[i]
            mass = self.find_mass_by_symbol(symbol)
            if mass is None:
                i += 1
                continue
            if i + 1 < len(self.chemical_equation) and self.chemical_equation[i + 1].isdigit():
                count = int(self.chemical_equation[i + 1])
                total_mass += mass * count
                i += 2
            else:
                total_mass += mass
                i += 1
        return total_mass

    def find_elements_info(self):
        info_list = []
        for element in set(self.chemical_equation):
            if element.isdigit():
                continue
            for name, data in self.elements_dict.items():
                if data["symbol"] == element:
                    chemical_element = ChemicalElement(
                        name, data["number"], data["symbol"], data["weight"],
                        data["boil"], data["melt"], data["density"], data["vapour"], data["fusion"]
                    )
                    info_list.append(str(chemical_element))
        return info_list


def text_to_list(user_request):
    result = []
    skip = False
    num_buffer = ""

    for index, element in enumerate(user_request):
        if skip:
            skip = False
            continue
        if index != len(user_request)-1:
            if element.isupper() and user_request[index + 1].islower():
                if num_buffer:
                    result.append(num_buffer)
                    num_buffer = ""
                result.append(user_request[index:index+2])
                skip = True
            elif element.isupper():
                if num_buffer:
                    result.append(num_buffer)
                    num_buffer = ""
                result.append(element)
            elif element.isdigit():
                num_buffer += element
        else:
            if element.isdigit():
                num_buffer += element
            else:
                if num_buffer:
                    result.append(num_buffer)
                    num_buffer = ""
                result.append(element)
    if num_buffer:
        result.append(num_buffer)
    return result


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id != CHANNEL_ID:
        return

    user_request = message.content.strip()
    parsed_list = text_to_list(user_request)
    service = ChemicalElementService(parsed_list)

    total_mass = service.calculate_mass()
    elements_info = service.find_elements_info()

    response = f"**Your requested chemical formula molar mass is:** {total_mass:.3f} g/mol\n\n"
    response += "**Elements Info:**\n"
    for info in elements_info:
        response += f"```\n{info}\n```\n"

    await message.channel.send(response)


bot.run(TOKEN)

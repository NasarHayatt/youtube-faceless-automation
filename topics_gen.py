import json, os
Q = "queue"
os.makedirs(Q, exist_ok=True)
SRC_SPACE = "Images: NASA. Narration and graphics were generated with AI. Figures are from public sources and rounded."
SRC_MATH = "Graphics and narration were generated with AI. The maths is shown so you can check it yourself."


def nasa(vo, q, big, label, sub, color, skip=0):
    return {"vo": vo, "bg": {"type": "nasa_img", "query": q, "skip": skip}, "big": big, "label": label, "sub": sub, "color": list(color)}


def plain(vo, big, label, sub, color, c1=(10, 8, 40), c2=(70, 20, 90)):
    return {"vo": vo, "bg": {"type": "plain", "c1": list(c1), "c2": list(c2)}, "big": big, "label": label, "sub": sub, "color": list(color)}


def out(t, space=True):
    if space:
        return nasa("Follow for more of the numbers behind " + t + ".", "nebula hubble", "", "", "Your Channel", (255, 255, 255), 2)
    return plain("Follow for more of the numbers behind " + t + ".", "", "", "Your Channel", (255, 255, 255))


topics = []


def add(slug, title, desc, tags, scenes, space=True):
    topics.append({"slug": slug, "title": title, "description": desc + "\n\n" + (SRC_SPACE if space else SRC_MATH) + "\n\n" + " ".join("#" + t for t in tags + ["shorts"]), "scenes": scenes, "kind": "short"})


add("parker-numbers", "Parker Solar Probe by the Numbers: The Fastest Thing Humans Ever Built",
    "Parker Solar Probe passed the Sun at about 692,000 km/h and about 6.1 million km from its surface.", ["space", "nasa", "sun"], [
        nasa("The fastest object humans have ever built is a probe that flies into the Sun's atmosphere.", "Parker Solar Probe", "692,000 km/h", "top speed", "Parker Solar Probe, December 2024", (255, 170, 60)),
        nasa("At its closest, it passed just six point one million kilometers from the solar surface.", "solar corona eclipse", "6.1M km", "closest approach", "Inside the Sun's atmosphere", (255, 210, 90), 1),
        nasa("Its heat shield, only eleven centimeters thick, faces temperatures near one thousand four hundred degrees Celsius.", "Parker Solar Probe heat shield", "1,400 C", "outside the heat shield", "Yet the instruments stay near room temperature", (255, 120, 90)),
        out("the Sun")])
add("apollo11-numbers", "Apollo 11 by the Numbers: 21 Hours and 36 Minutes on the Moon",
    "Apollo 11 landed on July 20, 1969 and brought back about 21.5 kg of lunar samples.", ["apollo11", "moon", "nasa"], [
        nasa("On July twentieth, nineteen sixty nine, humans first set foot on another world.", "Apollo 11 Buzz Aldrin on the moon", "1969", "the year", "Apollo 11, July 20", (255, 210, 90)),
        nasa("Neil Armstrong and Buzz Aldrin spent about twenty one hours and thirty six minutes on the lunar surface.", "Apollo 11 lunar module Eagle", "21h 36m", "on the Moon", "Two of the three crew landed", (120, 200, 255), 1),
        nasa("They brought back about twenty one and a half kilograms of Moon rock and soil.", "Apollo 11 lunar sample", "21.5 kg", "lunar samples", "Still studied today", (255, 150, 150)),
        out("the Moon landings")])
add("sun-numbers", "The Sun by the Numbers: 99.86% of Everything in Our Solar System",
    "The Sun holds about 99.86 percent of the solar system's mass and its light takes 8 minutes 20 seconds to reach Earth.", ["sun", "space", "nasa"], [
        nasa("The Sun is not just big. It is almost everything.", "the sun solar flare", "99.86%", "of the solar system's mass", "The planets share the last 0.14%", (255, 170, 60)),
        nasa("More than a million Earths could fit inside it.", "sun and earth size comparison", "1.3 million", "Earths fit inside", "By volume", (255, 210, 90), 1),
        nasa("Its light takes eight minutes and twenty seconds to reach us.", "sunrise from space", "8 min 20 s", "sunlight travel time", "150 million km away", (255, 190, 110)),
        out("our Sun")])
add("andromeda-numbers", "Andromeda by the Numbers: Our Nearest Big Galaxy Is Coming Closer",
    "Andromeda is about 2.5 million light-years away and approaching the Milky Way at about 110 km per second.", ["andromeda", "galaxy", "space"], [
        nasa("Look up on a very dark night and you can see another galaxy with your own eyes.", "Andromeda galaxy", "2.5M", "light-years away", "The Andromeda Galaxy", (200, 150, 255)),
        nasa("The light you see left it two and a half million years ago.", "Andromeda galaxy Hubble", "2.5M years", "old light", "Before modern humans existed", (255, 210, 90), 1),
        nasa("It is moving toward us at about one hundred ten kilometers every second, and the two galaxies are expected to merge in billions of years.", "Milky Way Andromeda collision", "110 km/s", "approaching speed", "A merger billions of years away", (120, 200, 255)),
        out("galaxies")])
add("blackhole-numbers", "Our Black Hole by the Numbers: Sagittarius A* in 3 Facts",
    "Sagittarius A* is about 26,000 light-years away and holds around 4 million times the mass of the Sun.", ["blackhole", "space", "milkyway"], [
        nasa("At the center of our galaxy sits a supermassive black hole.", "Sagittarius A* black hole Event Horizon Telescope", "4 million", "Suns of mass", "Sagittarius A*", (255, 130, 90)),
        nasa("It is about twenty six thousand light-years from Earth.", "Milky Way galactic center", "26,000", "light-years away", "Near the center of the Milky Way", (200, 150, 255), 1),
        nasa("In twenty twenty two scientists released the first image of it, built from radio telescopes working together.", "Event Horizon Telescope image", "2022", "first image released", "Using telescopes around the world", (255, 210, 90)),
        out("black holes")])
add("hubble-numbers", "Hubble by the Numbers: 35 Years Above the Atmosphere",
    "Hubble launched in 1990, orbits about 540 km above Earth at roughly 27,000 km/h.", ["hubble", "space", "nasa"], [
        nasa("The Hubble Space Telescope launched in nineteen ninety, and it is still working.", "Hubble Space Telescope in orbit", "1990", "launch year", "Over three decades of images", (255, 210, 90)),
        nasa("It circles the Earth about five hundred forty kilometers up, at roughly twenty seven thousand kilometers per hour.", "Hubble Space Telescope servicing mission", "27,000 km/h", "orbital speed", "One orbit about every 95 minutes", (120, 200, 255), 1),
        nasa("Its images have helped show that the universe is more than thirteen billion years old.", "Hubble Ultra Deep Field", "13.8 billion", "years: age of the universe", "Estimated with Hubble data", (255, 150, 200)),
        out("space telescopes")])

add("compound-numbers", "Compound Interest by the Numbers: $1,000 Becomes $7,612",
    "At 7 percent a year for 30 years, 1,000 dollars grows to about 7,612 dollars. The maths: 1,000 x 1.07^30 = 7,612.", ["money", "investing", "maths"], [
        plain("Here is why starting early matters so much. Put one thousand dollars away at seven percent a year.", "$1,000", "start", "7% a year, no extra deposits", (110, 220, 160), (6, 30, 30), (10, 80, 70)),
        plain("After ten years it is about one thousand nine hundred sixty seven dollars.", "$1,967", "after 10 years", "1,000 x 1.07^10", (255, 210, 90), (6, 30, 30), (10, 80, 70)),
        plain("After thirty years, the same money is worth about seven thousand six hundred twelve dollars. The last ten years add more than the first twenty.", "$7,612", "after 30 years", "1,000 x 1.07^30", (255, 150, 90), (6, 30, 30), (10, 80, 70)),
        out("money and maths", False)], False)
add("rule72-numbers", "The Rule of 72: How Fast Does Money Double?",
    "Divide 72 by the yearly return to estimate years to double: 72 / 6 = 12, 72 / 9 = 8.", ["money", "investing", "maths"], [
        plain("There is a quick trick to estimate how long money takes to double. It is called the rule of seventy two.", "72", "divide by your return", "Years to double = 72 / rate", (110, 220, 160), (10, 8, 40), (40, 30, 110)),
        plain("At six percent a year, seventy two divided by six is twelve years.", "12 years", "at 6% a year", "72 / 6 = 12", (255, 210, 90), (10, 8, 40), (40, 30, 110)),
        plain("At nine percent, it is just eight years. A few percent changes everything over time.", "8 years", "at 9% a year", "72 / 9 = 8", (255, 150, 150), (10, 8, 40), (40, 30, 110)),
        out("money and maths", False)], False)
add("birthday-numbers", "The Birthday Paradox: Only 23 People Needed for a 50% Match",
    "With 23 people, the chance that two share a birthday is about 50.7 percent. With 70 people it is about 99.9 percent.", ["maths", "probability", "paradox"], [
        plain("How many people do you need in a room before two probably share a birthday? Most people guess about one hundred eighty three.", "183?", "most people guess", "Half of 365", (255, 210, 90), (30, 8, 40), (100, 20, 100)),
        plain("The real answer is just twenty three. That gives about a fifty point seven percent chance.", "23", "people for a 50.7% chance", "Because there are 253 pairs to compare", (110, 220, 160), (30, 8, 40), (100, 20, 100)),
        plain("With seventy people, the chance is above ninety nine point nine percent.", "99.9%", "with 70 people", "Pairs grow much faster than people", (255, 150, 150), (30, 8, 40), (100, 20, 100)),
        out("maths and probability", False)], False)
add("rubik-numbers", "The Rubik's Cube by the Numbers: 43 Quintillion Positions",
    "A 3x3 cube has 43,252,003,274,489,856,000 possible positions, yet any one can be solved in at most 20 moves.", ["rubikscube", "maths", "puzzle"], [
        plain("A standard Rubik's Cube can be scrambled in forty three quintillion ways.", "43 quintillion", "possible positions", "43,252,003,274,489,856,000", (255, 210, 90), (8, 20, 50), (20, 70, 140)),
        plain("Yet in twenty ten, researchers proved that any scramble can be solved in twenty moves or fewer.", "20", "moves at most", "Known as God's Number", (110, 220, 160), (8, 20, 50), (20, 70, 140)),
        plain("If you tried one position every second, it would take more than a trillion years to see them all.", "1+ trillion", "years at one per second", "About 1.4 trillion years", (255, 150, 150), (8, 20, 50), (20, 70, 140)),
        out("maths and puzzles", False)], False)
add("chess-numbers", "Chess by the Numbers: 400 Positions After One Move Each",
    "After one move each there are 400 possible positions, and Claude Shannon estimated about 10^120 possible games.", ["chess", "maths", "numbers"], [
        plain("Chess starts simple. White has exactly twenty possible first moves.", "20", "first moves for White", "16 pawn moves and 4 knight moves", (255, 210, 90), (20, 10, 10), (90, 50, 20)),
        plain("After Black replies, there are four hundred possible positions. And it explodes from there.", "400", "positions after one move each", "20 x 20", (110, 220, 160), (20, 10, 10), (90, 50, 20)),
        plain("Claude Shannon estimated about ten to the power of one hundred twenty possible games, far more than atoms in the observable universe.", "10^120", "possible games, estimated", "Shannon number, 1950", (255, 150, 150), (20, 10, 10), (90, 50, 20)),
        out("maths and games", False)], False)
add("heart-numbers", "Your Heart by the Numbers: 100,000 Beats a Day",
    "A resting heart beats about 100,000 times a day, which is about 2.5 to 3 billion beats in a lifetime.", ["health", "science", "numbers"], [
        plain("Your heart never takes a day off.", "100,000", "beats a day, roughly", "At about 70 beats per minute", (255, 110, 130), (30, 8, 20), (110, 20, 50)),
        plain("Over a year that adds up to around thirty seven million beats.", "37 million", "beats a year", "70 x 60 x 24 x 365 = 36.8 million", (255, 210, 90), (30, 8, 20), (110, 20, 50)),
        plain("Across a long life, that is roughly two and a half to three billion beats.", "2.5 to 3 billion", "beats in a lifetime", "Without you ever thinking about it", (255, 150, 150), (30, 8, 20), (110, 20, 50)),
        out("the human body", False)], False)

for t in topics:
    json.dump(t, open(f"{Q}/{t['slug']}.json", "w", encoding="utf-8"), indent=1)
print(len(topics), "topics written to", Q)

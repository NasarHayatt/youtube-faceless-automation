import json, os
Q = "queue"
SP = "Images: NASA. Narration and graphics were generated with AI. Figures are from public sources and rounded."
MA = "Narration and graphics were generated with AI. The maths is shown so you can check it yourself."


def n(vo, q, big, label, sub, color, skip=0):
    return {"vo": vo, "bg": {"type": "nasa_img", "query": q, "skip": skip}, "big": big, "label": label, "sub": sub, "color": list(color)}


def p(vo, big, label, sub, color, c1, c2):
    return {"vo": vo, "bg": {"type": "plain", "c1": list(c1), "c2": list(c2)}, "big": big, "label": label, "sub": sub, "color": list(color)}


def outro(sp=True):
    if sp:
        return n("Subscribe for more of the numbers behind our world.", "nebula hubble", "", "", "Subscribe for more", (255, 255, 255), 2)
    return p("Subscribe for more of the numbers behind our world.", "", "", "Subscribe for more", (255, 255, 255), (10, 8, 40), (50, 30, 110))


items = []


def add(slug, title, desc, tags, scenes, space=True):
    items.append({"slug": slug, "format": "wide", "kind": "video", "title": title,
                  "description": desc + "\n\n" + (SP if space else MA) + "\n\n" + " ".join("#" + t for t in tags),
                  "scenes": scenes})


add("w-moon", "The Moon in 6 Numbers", "Distance, gravity, travel time and the 12 people who have walked there.", ["moon", "space", "nasa"], [
    n("The Moon is our nearest neighbor, but the numbers behind it are surprising. Here are six.", "full moon", "6", "numbers about the Moon", "", (220, 220, 255)),
    n("It orbits about three hundred eighty four thousand kilometers away, roughly thirty Earths in a row.", "moon from earth", "384,400 km", "average distance", "About 30 Earths wide", (255, 210, 90), 1),
    n("Its gravity is only one sixth of ours, so a hundred kilogram astronaut weighs about seventeen.", "moon surface astronaut", "1/6", "of Earth gravity", "A 100 kg person weighs about 17 kg", (120, 200, 255)),
    n("One lap around the Earth takes twenty seven point three days.", "moon phases", "27.3 days", "one orbit", "The same face always points at us", (255, 150, 150)),
    n("Apollo astronauts needed about three days to get there.", "Apollo 11 launch Saturn V", "3 days", "travel time, Apollo", "Launched July 16, 1969", (255, 170, 60)),
    n("Only twelve people have ever walked on its surface, between nineteen sixty nine and nineteen seventy two.", "Apollo 17 astronaut moon", "12", "people on the Moon", "1969 to 1972", (200, 150, 255)),
    outro()])
add("w-mars", "Mars in 6 Numbers", "Day length, year length, gravity and the tallest volcano in the solar system.", ["mars", "space", "nasa"], [
    n("Mars feels familiar and alien at the same time. Here are six numbers that show why.", "Mars planet", "6", "numbers about Mars", "", (255, 140, 90)),
    n("A day on Mars lasts twenty four hours and thirty seven minutes, almost the same as ours.", "Mars rover panorama", "24h 37m", "one Martian day", "37 minutes longer than Earth", (255, 190, 110), 1),
    n("But its year is six hundred eighty seven Earth days, nearly twice as long.", "Mars Hubble", "687 days", "one Martian year", "Almost 2 Earth years", (255, 150, 90)),
    n("Gravity there is about thirty eight percent of what we feel on Earth.", "Curiosity rover selfie", "38%", "of Earth gravity", "You would feel much lighter", (120, 200, 255)),
    n("Olympus Mons is about twenty two kilometers tall, nearly three times the height of Everest.", "Olympus Mons", "22 km", "Olympus Mons", "About 3x Mount Everest", (255, 110, 110)),
    n("Signals between Earth and Mars take from about three to twenty two minutes, depending on where the planets are.", "Mars Perseverance rover", "3 to 22 min", "one-way radio delay", "Depends on orbital positions", (200, 150, 255)),
    outro()])
add("w-iss", "The International Space Station in 6 Numbers", "Speed, altitude, sunrises per day and continuous crew since 2000.", ["iss", "space", "nasa"], [
    n("The International Space Station is the largest object humans have ever put in orbit. Here are six numbers.", "international space station", "6", "numbers about the ISS", "", (90, 220, 255)),
    n("It travels at about seventeen thousand five hundred miles per hour.", "ISS over earth", "17,500 mph", "orbital speed", "About 28,000 km/h", (255, 210, 90), 1),
    n("It flies roughly four hundred kilometers above the ground.", "ISS earth horizon", "400 km", "altitude", "About 250 miles up", (120, 200, 255)),
    n("One orbit takes about ninety minutes, so the crew sees about sixteen sunrises every day.", "sunrise from space station", "16", "sunrises a day", "One orbit every 90 minutes", (255, 170, 60)),
    n("People have lived aboard continuously since November two thousand.", "astronaut spacewalk ISS", "Nov 2000", "continuously crewed since", "More than 25 years", (255, 150, 150)),
    n("It is about the size of an American football field, including its solar arrays.", "ISS solar arrays", "109 m", "length of the station", "About 357 feet", (200, 150, 255)),
    outro()])
add("w-jupiter", "Jupiter in 6 Numbers", "Size, storm, day length, year length and mass compared with the other planets.", ["jupiter", "space", "nasa"], [
    n("Jupiter is the giant of our solar system. Here are six numbers that show how big it really is.", "Jupiter planet", "6", "numbers about Jupiter", "", (255, 190, 120)),
    n("More than thirteen hundred Earths could fit inside it.", "Jupiter Earth size comparison", "1,300", "Earths fit inside", "By volume", (255, 210, 90), 1),
    n("Its Great Red Spot is a storm wider than our entire planet.", "Jupiter Great Red Spot", "1.3x", "wider than Earth", "A storm seen for centuries", (255, 110, 110)),
    n("A day on Jupiter lasts under ten hours, the shortest of any planet.", "Jupiter Juno", "9h 56m", "one Jupiter day", "The fastest spinning planet", (120, 200, 255)),
    n("But one trip around the Sun takes almost twelve Earth years.", "Jupiter Hubble", "11.9 years", "one Jupiter year", "Around the Sun once", (255, 170, 60)),
    n("Its mass is about two and a half times all the other planets combined.", "Jupiter and moons", "2.5x", "all other planets together", "By mass", (200, 150, 255)),
    outro()])
add("w-compound", "Compound Interest in 5 Numbers", "How 1,000 dollars grows at 7 percent a year: the maths shown step by step.", ["money", "investing", "maths"], [
    p("Compound interest is the most powerful idea in personal finance. Here it is in five numbers.", "5", "numbers, one idea", "$1,000 at 7% a year", (110, 220, 160), (6, 30, 30), (10, 80, 70)),
    p("Start with one thousand dollars and add nothing else.", "$1,000", "starting amount", "No extra deposits", (255, 210, 90), (6, 30, 30), (10, 80, 70)),
    p("After ten years you have about one thousand nine hundred sixty seven dollars.", "$1,967", "after 10 years", "1,000 x 1.07^10", (120, 200, 255), (6, 30, 30), (10, 80, 70)),
    p("After twenty years, about three thousand eight hundred seventy.", "$3,870", "after 20 years", "1,000 x 1.07^20", (255, 170, 60), (6, 30, 30), (10, 80, 70)),
    p("After thirty years, about seven thousand six hundred twelve. The last ten years add more than the first twenty combined.", "$7,612", "after 30 years", "1,000 x 1.07^30", (255, 110, 110), (6, 30, 30), (10, 80, 70)),
    p("The lesson: time matters more than the amount. Start early and let it grow.", "TIME", "beats amount", "Start early", (200, 150, 255), (6, 30, 30), (10, 80, 70)),
    outro(False)], False)
add("w-chess", "Chess in 5 Numbers", "Opening moves, positions after one move each, and the Shannon number.", ["chess", "maths", "numbers"], [
    p("Chess looks simple, but the numbers behind it are enormous. Here are five.", "5", "numbers about chess", "The maths of a board game", (255, 210, 90), (20, 10, 10), (90, 50, 20)),
    p("White starts with exactly twenty legal first moves.", "20", "first moves for White", "16 pawn moves and 4 knight moves", (110, 220, 160), (20, 10, 10), (90, 50, 20)),
    p("After one move each, there are four hundred possible positions.", "400", "positions after move one", "20 x 20", (120, 200, 255), (20, 10, 10), (90, 50, 20)),
    p("After two moves each, there are about one hundred ninety seven thousand possible move sequences.", "197,281", "move sequences after two moves each", "Growing explosively", (255, 170, 60), (20, 10, 10), (90, 50, 20)),
    p("Claude Shannon estimated about ten to the one hundred twentieth possible games, far more than atoms in the universe.", "10^120", "possible games, estimated", "Shannon number, 1950", (255, 110, 110), (20, 10, 10), (90, 50, 20)),
    outro(False)], False)

for it in items:
    json.dump(it, open(f"{Q}/{it['slug']}.json", "w", encoding="utf-8"), indent=1)
print(len(items), "wide topics written")

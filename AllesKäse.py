from typing import Iterator
import sys
import math

Scheibe = tuple[int, int]

# Liest alle Textfiles bis max ein und gibt mehrere Eigenschaften der Datei zurück
# - ein Dictionary mit allen Käsescheiben und wie oft sie vorkommen
# - eine Liste mit den Käsescheiben mit der kürzesten Kantenlänge
# - die Anzahl an gegebenen Käsescheiben
def read_text_files(max: int) -> Iterator[tuple[dict[Scheibe, int], list[Scheibe], int]]:
    for i in range(1, max + 1):
        min_size = math.inf
        min_scheiben = []
        kaese_scheiben = {}
        counter = None
        with open("kaese" + str(i) + ".txt") as file:
            counter = int(next(file))
            for line in file:
                scheibe = line.replace("\n", "").split(" ")
                my_tuple = (int(scheibe[0]), int(scheibe[1]))
                if my_tuple[0] < min_size:
                    min_size = my_tuple[0]
                    min_scheiben = [my_tuple]
                elif my_tuple[0] == min_size and my_tuple not in min_scheiben:
                    min_scheiben += [my_tuple]
                if my_tuple in kaese_scheiben.keys():
                    kaese_scheiben[my_tuple] += 1
                else:
                    kaese_scheiben[my_tuple] = 1
        yield kaese_scheiben, min_scheiben, counter

# Nimmt eine Käsescheibe und die aktuelle Größe des Käseblockes und gibt die Seite des Blockes zurück,
# die sich vergrößert, wenn die Käsescheibe dem Block hinzugefügt wird (0, 1 oder 2) 
# bsp: (1, 2), [1, 2, 3] -> 2 (index von Element 3)
def get_seite(scheibe: Scheibe, size: list[int]) -> int:
    x = size.index(scheibe[0])
    y = size.index(scheibe[1])
    if x == y:
        for elm in range(3):
            if size[elm] != scheibe[0]:
                return elm
    for elm in range(3):
        if elm != x and elm != y:
            return elm

# Findet ausgehend von einem gegebenen Dictionary von Käsescheiben und deren kleinsten Scheiben alle möglichen
# Anfangskäseblöcke bsp: [(6, 7), (6, 7), (2, 7)]
# (Generator -> errechnet den nächsten Anfangsblock nur, wenn noch keine Zusammensetzung des Blockes gefunden wurde)
def find_possible_first_blocks(kaese_scheiben: dict[Scheibe, int], min_scheiben) -> Iterator[list[Scheibe]]:
    for min_scheibe in min_scheiben:
        for scheibe in kaese_scheiben.keys():
            if min_scheibe[1] in scheibe and ((kaese_scheiben[scheibe] >= min_scheibe[0] and scheibe != min_scheibe) or kaese_scheiben[scheibe] > min_scheibe[0]):
                l = [scheibe[0], scheibe[1], min_scheibe[0]]
                index = get_seite(min_scheibe, l)
                l[index] += 1
                yield [scheibe for i in range(min_scheibe[0])] + [min_scheibe], l
        yield [min_scheibe], [min_scheibe[0], min_scheibe[1], 1]

# Findet ausgehend von der aktuellen Größe des Käseblocks alle passenden Scheiben
def find_possibles(size_cube: list[int]) -> list[tuple[int, int]]:
    s = sorted(size_cube)
    return [(s[0], s[1]), (s[0], s[2]), (s[1], s[2])]

# Versucht rekursiv den orginalen Käsewürfel mit einem gegebenen Anfangswürfel zu rekonstruieren.
# Die richtige Anordnung wird dabei in my_order gespeichert,
# fehlende Scheiben -falls erlaubt- in missing_scheiben
# Wenn keine Lösung wird False zurückgegeben
def find_original_cube(size_cube: list[int], kaese_scheiben: dict[Scheibe, int], counter: int, 
                       my_order: list[Scheibe], missing_scheiben_allowed: int, missing_scheiben: list[Scheibe], 
                       new_cubes_allowed: int, combination_scheiben_allowed: int) -> tuple[list[Scheibe], int, list[Scheibe], int] | bool:
    ######################################################
    ## returnt Ergebnis wenn alle Scheiben verbaut sind ##
    if counter == 0:
        return my_order, missing_scheiben_allowed, missing_scheiben, new_cubes_allowed, combination_scheiben_allowed
    possibles = find_possibles(size_cube)
    is_allowed_anyways = False
    #######################
    ## algorithmen aus b ##
    if not any(map(lambda x: kaese_scheiben.get(x, 0) > 0, possibles)):
        #######################
        ## Käsescheibe fehlt ##
        if missing_scheiben_allowed > 0:
            is_allowed_anyways = True
            missing_scheiben_allowed -= 1
        ##########################
        ## Scheiben kombinieren ##
        elif combination_scheiben_allowed > 0:
            for scheibe1 in kaese_scheiben.keys():
                if kaese_scheiben[scheibe1] != 0:
                    kaese_scheiben[scheibe1] -= 1
                    for scheibe2 in kaese_scheiben.keys():
                        if kaese_scheiben[scheibe2] != 0:
                            option = None
                            if scheibe2[0] == scheibe1[0]:
                                option = tuple(sorted((scheibe1[0], scheibe1[1] + scheibe2[1])))
                            elif scheibe2[1] == scheibe1[0]:
                                option = tuple(sorted((scheibe1[0], scheibe1[1] + scheibe2[0])))
                            elif scheibe2[0] == scheibe1[1]:
                                option = tuple(sorted((scheibe1[1], scheibe1[0] + scheibe2[1])))
                            elif scheibe2[1] == scheibe1[1]:
                                option = tuple(sorted((scheibe1[1], scheibe1[0] + scheibe2[0])))
                            if option in possibles:
                                kaese_scheiben[scheibe1] -= 1
                                kaese_scheiben[scheibe2] -= 1
                                counter -= 2
                                index = get_seite(option, size_cube)
                                my_order += [option]
                                size_cube[index] += 1
                                result = find_original_cube(size_cube, kaese_scheiben, counter, my_order, missing_scheiben_allowed, missing_scheiben, new_cubes_allowed, combination_scheiben_allowed - 1)
                                if not result:
                                    del my_order[-1]
                                    size_cube[index] -= 1
                                    kaese_scheiben[scheibe1] += 1
                                    kaese_scheiben[scheibe2] += 1
                                    counter += 2
                                else:
                                    return result
                    kaese_scheiben[scheibe1] += 1
            return False
        ###########################
        ## neuen Würfel anfangen ##
        elif new_cubes_allowed > 0:
            min_size = math.inf
            min_scheiben = []
            for my_tuple in kaese_scheiben.keys():
                if kaese_scheiben[my_tuple] != 0:
                    if my_tuple[0] < min_size:
                        min_size = my_tuple[0]
                        min_scheiben = [my_tuple]
                    elif my_tuple[0] == min_size and my_tuple not in min_scheiben:
                        min_scheiben += [my_tuple]
            res = get_solution(kaese_scheiben, min_scheiben, counter, missing_scheiben_allowed, new_cubes_allowed - 1, combination_scheiben_allowed)
            if not res:
                return False
            else:
                return my_order + res[0], res[1], missing_scheiben + res[2], new_cubes_allowed - 1, combination_scheiben_allowed
    ##########################
    ## normaler Algorithmus ##
    for elm in possibles:
        if kaese_scheiben.get(elm, 0) != 0 or is_allowed_anyways:
            index = get_seite(elm, size_cube)
            if not is_allowed_anyways:
                kaese_scheiben[elm] -= 1
                counter -= 1
            else:
                missing_scheiben += [elm]
            my_order += [elm]
            size_cube[index] += 1
            result = find_original_cube(size_cube, kaese_scheiben, counter, my_order, missing_scheiben_allowed, missing_scheiben, new_cubes_allowed, combination_scheiben_allowed)
            if not result:
                del my_order[-1]
                size_cube[index] -= 1
                if not is_allowed_anyways:
                    counter += 1
                    kaese_scheiben[elm] += 1
                else:
                    del missing_scheiben[-1]
            else:
                return result
    return False

# Wendet find_possible_first_blocks und anschließend find_original_cube an, um den ursprünglichen
# Käsequarder zu rekonstruieren
# Wenn nur gleiche Scheiben in den gegebenen Scheiben zu finden sind, werden diese als Antwort zurückgegeben
# bsp: (3, 4) (3, 4) -> [(3, 4), (3, 4)]
# Wenn keine Lösung wird False zurückgegeben
def get_solution(kaese_scheiben: dict[Scheibe, int], min_scheiben: list[Scheibe], counter: int,
                 missing_scheiben_allowed: int, new_cubes_allowed: int, combination_scheiben_allowed: int) -> tuple[list[Scheibe], int, list[Scheibe], int] | bool:
    my_first_blocks = find_possible_first_blocks(kaese_scheiben, min_scheiben)
    for elm in my_first_blocks:
        my_order = elm[0][:]
        for e in elm[0]:
            kaese_scheiben[e] -= 1
            counter -= 1
        res = find_original_cube(elm[1], kaese_scheiben, counter, my_order, missing_scheiben_allowed, [], new_cubes_allowed, combination_scheiben_allowed)
        if not res:
            for e in elm[0]:
                kaese_scheiben[e] += 1
                counter += 1
        else:
            return res
    else:
        return False

# Führt alles in der richtigen Reihenfolge aus und druckt die Ergebnisse auf die Konsole.
# Parameter:
#   - amount_textfiles: alle Datein mit kaese[i].txt mit i bis einschließlich _ werden ausgelesen
#   - missing_scheiben_allowed: wie viele Scheiben in der Lösung maximal gegessen worden sein dürfen
#   - new_cubes_allowed: wie viele neue Käsewürfel maximal angefangen werden dürfen
if __name__ == "__main__":
    sys.setrecursionlimit(1530000)
    amount_textfiles = 15
    text_files = read_text_files(amount_textfiles)
    for i, (kaese_scheiben, min_scheiben, counter) in enumerate(text_files):
        if i <= 6 or i == 8:
            missing_scheiben_allowed = 0
            new_cubes_allowed = 0
            combination_scheiben_allowed = 0
        elif i == 7:
            missing_scheiben_allowed = 1
            new_cubes_allowed = 0
            combination_scheiben_allowed = 0
        elif i == 13:
            missing_scheiben_allowed = 2
            new_cubes_allowed = 0
            combination_scheiben_allowed = 0
        elif i > 8 and i < 12:
            missing_scheiben_allowed = 0
            new_cubes_allowed = 1
            combination_scheiben_allowed = 0
        elif i == 14:
            missing_scheiben_allowed = 0
            new_cubes_allowed = 2
            combination_scheiben_allowed = 0
        else:
            missing_scheiben_allowed = 0
            new_cubes_allowed = 0
            combination_scheiben_allowed = 1
        s = get_solution(kaese_scheiben, min_scheiben, counter, missing_scheiben_allowed, new_cubes_allowed, combination_scheiben_allowed)   
        print(f"___________________\nkaese{i + 1}:")
        if not s:
            print("not possible\n___________________")
        else:
            n = 0
            for elm in s[0]:
                if n < 10:
                    print(elm, end=" ")
                    n += 1
                else:
                    print("...", end="")
                    break
            used = missing_scheiben_allowed - s[1]
            if used > 0:
                print(f"\nAnzahl fehlender Scheiben: {used} -> {s[2]}", end="")
            used = new_cubes_allowed - s[3]
            if used > 0:
                print(f"\nAnzahl Kaesewuerfel: {used + 1}", end="")
            used = combination_scheiben_allowed - s[4]
            if used > 0:
                print(f"\nAnzahl Zusammengesetzte: {used}", end="")
            print("\n___________________")
import enum
import math
import os
# import lxml
from lxml import etree
from numpy import array_split, double

class CalculateStatus(enum.Enum):
    NoneXML = -1


class Criteria(enum.Enum):
    Speed = "speed"
    Displacement = "displacement"
    Chord = "chord"
    Harmony = "harmony"
    Rhythm = "rhythm"
    Nbpages = "nbpages"
    Tonality = "tonality"

note_values = {"whole":1, "half":2, "quarter":4, "eighth":8, "16th":16, "32nd":32, "64th":64, "128th":128, "256th":256}

# pitch2int 将音符音高转换为数值
def pitch2int(pitch, note_octave, alter):
    pitch_value = 1
    if "A" == pitch:
        pitch_value = 10
    elif "B" == pitch:
        pitch_value = 12
    elif "C" == pitch:
        pitch_value = 1
    elif "D" == pitch:
        pitch_value = 3
    elif "E" == pitch:
        pitch_value = 5
    elif "F" == pitch:
        pitch_value = 6
    elif "G" == pitch:
        pitch_value = 8
    if None is not alter:
        pitch_value += alter
    if 1 == note_octave:
        pitch_value -= 36 # 3*12
    elif 2 == note_octave:
        pitch_value -= 24 # 2*12
    elif 3 == note_octave:
        pitch_value -= 12 # 1*12
    elif 5 == note_octave:
        pitch_value += 12 # 1*12
    elif 6 == note_octave:
        pitch_value += 24 # 2*12
    elif 7 == note_octave:
        pitch_value += 36 # 3*12
    elif 8 == note_octave:
        pitch_value += 48 # 4*12
    return pitch_value

# semitone2octave 将半音间距转换为八度间距
def semitone2octave(semitone_num):
    nb_octaves = math.floor(semitone_num/12)
    reste = semitone_num % 12
    return [nb_octaves, reste]

# at_same_time 检查同时按下的音符数
def at_same_time(note):
    result = []
    measure_nodes = note.xpath('parent::*')
    measure_node = measure_nodes[0]
    the_notes = measure_node.note
    notes_timecodes = []
    notes_timecodes.append([the_notes[0], 0])
    current_timecode = 0
    previous_note = the_notes[0]
    my_note_timecode = 0
    for i in len(the_notes):
        current_note = the_notes[i]
        if previous_note.staff != current_note.staff:
            current_timecode = 0
        elif not current_note.chord:
            current_timecode += previous_note.duration
        notes_timecodes.append([current_note, current_timecode])
        previous_note = current_note
        if current_note == note:
            my_note_timecode = current_timecode
    for i in len(notes_timecodes):
        tied = notes_timecodes[i][0].xpath("./notations/tied")
        if len(tied) != 0:
            tied = tied[0].attributes()
            if "stop" != tied:
                tied = False
        if notes_timecodes[i][0] != note and notes_timecodes[i][1] == my_note_timecode and not notes_timecodes[i][0].rest and not tied:
            result.append(notes_timecodes[i][0])
    return result

# get_note 返回一个音符
def get_note(xml, mes, n, staff):
    the_measure = xml.xpath(f"//measure[@number={mes}]")
    the_notes = the_measure[0].xpath(f"./note[staff={staff} and not(rest)]")
    if n < len(the_notes):
        return the_notes[-1] # n - 1
    else:
        return None

# get_measure 返回元素的父元素
def get_measure(xml, note):
    measure_nodes = note.xpath("parent::*")
    return measure_nodes[0]

# get_measure_number 返回元素的所在小节
def get_measure_number(xml, note):
    the_measure = get_measure(xml, note)
    measure_attributes = the_measure.find("attributes")
    # return measure_attributes["number"]
    if measure_attributes is None:
        return None
    else:
        # print(measure_attributes.find("number"))
        return measure_attributes.get("number")

# get_note_pos_in_mes 获取元素在五线谱上的位置
def get_note_pos_in_mes(xml, note):
    staff = note.find("staff").text
    the_measure = get_measure(xml, note)
    the_note = the_measure.xpath(f"./note[staff={staff}]")
    pos = 0
    found = False
    for k, v in enumerate(the_note):
        if v == note:
            found = True
            pos = k
            break
    if found:
        return pos
    else:
        return None

# get_previous_note_element 返回上一个音符，如果不存在则返回当前元素
def get_previous_note_element(xml, note):
    previous_note_prov = note
    pos = get_note_pos_in_mes(xml, note)
    staff = note.find("staff").text
    if None is not pos:
        if 1 == pos:
            mes = get_measure_number(xml, note)
            if mes is not None and mes > 1:
                the_measure = xml.xpath(f"//measure[@number={(mes-1)}]")
                the_notes_prov = the_measure[0].xpath(f"/note[staff={staff}]")
                if len(the_notes_prov) > 0:
                    previous_note_prov = the_notes_prov[-1] # len(the_notes_prov) - 1
                else:
                    while 0 == len(the_notes_prov):
                        mes -= 1
                        the_measure = xml.xpath(f"//measure[@number={(mes-1)}]")
                        the_notes_prov = the_measure[0].xpath(f"/note[staff={staff}]")
                    if len(the_notes_prov) > 0:
                        previous_note_prov = the_notes_prov[-1] # len(the_notes_prov) - 1
        else:
            mes_node = get_measure(xml, note)
            the_notes_prov = mes_node.xpath(f"./note[staff={staff}]")
            if len(the_notes_prov) > 0:
                # print(len(the_notes_prov), pos)
                previous_note_prov = the_notes_prov[pos-1]
    return previous_note_prov

# evaluate_difficulty 评估难度
def evaluate_difficulty(criteria, value, valueLH):
    result = 0
    resultLH = 0
    if Criteria.Speed == criteria:
        if value > 80:
            return 4
        elif value > 50:
            return 3
        elif value > 20:
            return 2
        else:
        # elif value > 10:
            return 1
    elif Criteria.Displacement == criteria:
        if value > 20:
            result = 4
        elif value > 10:
            result = 3
        elif value > 5:
            result = 2
        else:
            result = 1
        if valueLH > 55:
            resultLH = 4
        elif valueLH > 20:
            resultLH = 3
        elif valueLH > 10:
            resultLH = 2
        else:
            resultLH = 1
        if 2 == result:
            if 2 == resultLH:
                return 3
        if 3 == result:
            if 3 == resultLH:
                return 4
        return max(result, resultLH)
    elif Criteria.Chord == criteria:
        if value > 60:
            result = 4
        elif value > 30:
            result = 3
        elif value > 10:
            result = 2
        else:
            result = 1
        if valueLH > 60:
            resultLH = 4
        elif valueLH > 30:
            resultLH = 3
        elif valueLH > 10:
            resultLH = 2
        else:
            resultLH = 1
        if 2 == result:
            if 2 == resultLH:
                return 3
        if 3 == result:
            if 3 == resultLH:
                return 4
        return max(result, resultLH)
    elif Criteria.Harmony == criteria:
        if value > 30:
            result = 4
        elif value > 20:
            result = 3
        elif value > 5:
            result = 2
        else:
            result = 1
        if valueLH > 30:
            resultLH = 4
        elif valueLH > 20:
            resultLH = 3
        elif valueLH > 5:
            resultLH = 2
        else:
            resultLH = 1
        if 2 == result:
            if 2 == resultLH:
                return 3
        if 3 == result:
            if 3 == resultLH:
                return 4
        return max(result, resultLH)
    elif Criteria.Rhythm == criteria:
        if value > 60:
            return 4
        elif value > 20:
            return 3
        elif value > 0:
            return 2
        else:
            return 1
    elif Criteria.Nbpages == criteria:
        if value > 6:
            return 4
        elif value > 4:
            return 3
        elif value > 2:
            return 2
        else:
            return 1
    elif Criteria.Tonality == criteria:
        if value > 5:
            return 4
        elif value > 3:
            return 3
        elif value > 1:
            return 2
        else:
            return 1
        

def read_xml(path):
    return etree.parse(path)
    # data = None
    # with open(path) as f:
    #     data = f.read()
    # # print(type(data)) # str
    # if data is not None:
    #     return etree.XML(data)
    # else:
    #     return None

def cal_xml(path):
    # Meta Data
    xml = read_xml(path)
    if xml is None:
        print("error: read xml failed.")
        return CalculateStatus.NoneXML
    identification = xml.xpath("//identification")

    # Calculate page length.
    pages = xml.xpath("//print[@page-number]")
    pages_len = 0
    num_pages = []
    for page in pages:
        attr = page.find("attributes")
        if attr is not None:
            num_pages.append(attr.get("page-number"))
            # num_pages.append(page.attributes()['page-number']
    if len(num_pages) != 0:
        pages_len = len(num_pages)
    else:
        pages = xml.xpath("//print[@new-page=\"yes\"]")
        if len(pages) != 0:
            pages_len = len(pages) + 1
        else:
            pages_len = 1

    # Calculate measure
    measure = xml.xpath("//measure")
    measure_len = len(measure)
    
    # Calculate notes
    notes = xml.xpath("//note[not(rest)]")
    quantise = 4
    note_counter = 0
    note_counterRH = 0
    note_counterLH = 0
    base_duration = 10000
    note_proportions = []

    # Calculate note
    for note in notes:
        note_counter += 1
        if note.find("voice").text == "1":
            note_counterRH += 1
        else:
            note_counterLH += 1
        current_note_value = 0
        note_type = note.find("type").text
        current_note_value = note_values[note_type]
        
        if len(note.xpath("time-modification")) > 0:
            actual_note = note.xpath("time-modification/actual-notes")
            normal_note = note.xpath("time-modification/normal-notes")
            current_note_value *= (int(actual_note[0].text)/int(normal_note[0].text))
            # print(current_note_value)
        #

        # 统计不同类型的音符个数
        k = 0
        while k < len(note_proportions) and note_proportions[k][0] != current_note_value:
            k += 1
        if k < len(note_proportions):
            note_proportions[k][1] += 1
        else:
            note_proportions.append([current_note_value, 1])
        # print(note_proportions, k, len(note_proportions))
        if len(note.xpath("time-modification")) == 0:
            duration = note.find("duration")
            if duration is not None:
                the_note_duration = duration.text
                if the_note_duration != "":
                    if(int(the_note_duration) < int(base_duration)):
                        base_duration = duration.text
            if current_note_value > quantise:
                quantise = current_note_value
    

    tonality_p = xml.xpath("//key/fifths")
    tonality = tonality_p[0]
    # mode_p = xml.xpath("//key/mode")
    # mode = mode_p[0]
    tonality_string = "" # getTonality
    measure = xml.xpath("//measure")
    current_part = [1, len(measure), 100]
    parts = []
    parts.append(current_part)


    for k, v in enumerate(measure):
        new_part_score = 0
        current_measure = v
        attr = current_measure.find("attributes")
        if attr is not None:
            # print(attr.find("key"))
            if attr.find("key") is not None:
                new_part_score += 100
        if current_measure.find("direction") is not None:
            if len(current_measure.xpath("./direction[@placement=\"above\" and staff=1]")) != 0:
                if len(current_measure.xpath("./direction/direction-type/metronome")) != 0:
                    new_part_score += 80
        if len(current_measure.xpath("./sound[@tempo]")) != 0:
            new_part_score += 20
        addonmeasure = False
        if len(current_measure.xpath("./barline[@location=\"right\"]")) != 0:
            new_part_score += 50
            addonmeasure = True
        if new_part_score >= 50:
            if addonmeasure:
                parts[-1][1] = k+1
                parts.append([k+2, len(measure), math.floor(new_part_score / 260 * 100)])
            else:
                parts[-1][1] = k
                parts.append([k+1, len(measure), math.floor(new_part_score / 260 * 100)])
    
    
    aeffacter = []

    for k, v in enumerate(parts):
        if parts[k][1] - parts[k][0] < 2:
            parts[k - 1][1] = parts[k][1]
            aeffacter.append(k)
    i = len(aeffacter) - 1
    while i >= 0:
        # print(aeffacter[i])
        parts[aeffacter[i]] = 1
        i -= 1
    tempoP = xml.xpath("//@tempo")
    tempo = tempoP[0]
    beatsP  = xml.xpath("//beats")
    beats = beatsP[0]
    beat_typeP = xml.xpath("//beat-type")
    beat_type = beat_typeP[0]
    quickest_value = 1
    quickest_value_real = 1

    for k, v in enumerate(note_proportions):
        key = note_proportions[k][0]
        value = note_proportions[k][1]
        if key > quickest_value:
            if value > (0.15 * note_counter):
                quickest_value = key
            else:
                quickest_value_real = key
    rapidite = double(tempo) * quickest_value * 100 / 2816
    notesRH = xml.xpath("//note[staff=1 and not(rest)]")
    measure = 1
    note_num = 2
    accord = False
    deplacement_num = 0
    diff_deplacements = []
    accidental_notes = []
    time_modifications = []
    pitch = notesRH[0].find("pitch")
    # print(pitch)
    note_pitch_letter = pitch.get("step")
    note_octave = pitch.get("octave")
    alter = pitch.get("alter")

    if notesRH[0].find("accidental") is not None:
        accidental_notes.append([measure, 1, notesRH[0].find("accidental")])
    if len(notesRH[0].xpath("time-modification")) != 0:
        time_modifications.append(measure)
    
    num_chordRH = 0
    num_octavesRH = 0
    chord_base_value = 0
    previous_note = notesRH[0]
    previous_note_pitch = previous_note.find("pitch")
    previous_note_pitch_letter = pitch.get("step")
    previous_note_octave = pitch.get("octave")
    previous_notealter = pitch.get("alter")

    previous_note_pitch_value = pitch2int(previous_note_pitch_letter, previous_note_octave, previous_notealter)

    for k, v in enumerate(notesRH):
        note = v
        note_pitch = note.find("pitch")
        note_pitch_letter = pitch.get("step")
        note_octave = pitch.get("ocatve")
        alter = pitch.get("alter")
        note_pitch_value = pitch2int(note_pitch_letter, note_octave, alter)

        chord = note.find("chord")
        if chord is not None:
            deplacement_num += 1
            previous_note = get_previous_note_element(xml, previous_note)
            gap_duration = int(previous_note.find("duration").text)
            while previous_note.find("rest") is not None:
                p_note = get_previous_note_element(xml, previous_note)
                if p_note == previous_note:
                    break
                else:
                    previous_note = p_note
                gap_duration += int(previous_note.find("duration").text)
            while previous_note.find("chord") is not None:
                p_note = get_previous_note_element(xml, previous_note)
                if p_note == previous_note:
                    break
                else:
                    previous_note = p_note
                previous_note_pitch = previous_note.find("pitch")
                previous_note_pitch_letter = pitch.get("step")
                previous_note_octave = pitch.get("octave")
                previous_notealter = pitch.get("alter")

                previous_note_pitch_value = pitch2int(previous_note_pitch_value, previous_note_octave, previous_notealter)
        current_ecart = abs(note_pitch_value -  previous_note_pitch_value)
        
        measure_temp = get_measure_number(xml, note)

        # 
        if measure_temp != measure:
            note_num = 1
            measure = measure_temp
        if current_ecart > 12:
            if gap_duration <= base_duration * quickest_value / beat_type * 2:
                diff_deplacements.append([measure, note_num, current_ecart])
        if note.find("accidental") is not None:
            accidental_notes.append([measure, note_num, note.find("accidental")])
        if len(note.xpath("time-modification")) != 0:
            time_modifications.append(measure)
        if k < len(notesRH) - 1:
            if note.find("chord") is not None or ((note.find("chord") is None) and notesRH[k+1].find("chord") is not None):
                accord = True
                if note.find("chord") is None:
                    num_chordRH += 1
                    chord_base_value = note_pitch_value
                if note_pitch_value == chord_base_value + 12:
                    num_octavesRH += 1
            else:
                accord = False
        note_num += 1
    
    if len(diff_deplacements) > 0:
        max_ecart_droite = diff_deplacements[0]
        for k, v in enumerate(diff_deplacements):
            current_dep = v
            if current_dep[2] > max_ecart_droite[2]:
                max_ecart_droite = current_dep
        max_intervalRH = max_ecart_droite[0]
    else:
        max_ecart_droite = 0
        max_intervalRH = 0
    
    if deplacement_num != 0:
        displacementsRH = len(diff_deplacements) / deplacement_num * 100
    else:
        # TODO 检查这种情况下如何设置displacementsRH值
        displacementsRH = 0
    
    notesLH = xml.xpath("//note[staff=2 and not(rest)]")

    measure = 1
    note_num = 2
    accord = False
    deplacement_numLH = 0
    diff_deplacementsLH = []
    accidental_notesLH = []
    time_modificationsLH = []

    note_pitch = notesLH[0].find("pitch")
    note_pitch_letter = note_pitch.get("step")
    note_octave = note_pitch.get("octave")
    alter = note_pitch.get("alter")

    previous_note_octave = note_octave
    previous_notealter = alter
    previous_note_pitch_value = note_pitch_value

    if notesLH[0].find("accidental") is not None:
        accidental_notesLH.append([measure, 1, notesLH[0].find("accidental")])
    if len(notesLH[0].xpath("time-modification")) != 0:
        time_modificationsLH.append(measure)
    num_chordLH = 0
    num_octavesLH = 0
    chord_base_value = 0
    previous_note = notesLH[0]

    for k, v in enumerate(notesLH):
        note = v
        note_pitch = note.find("pitch")
        note_pitch_letter = note_pitch.get("step")
        note_octave = note_pitch.get("octave")
        alter = note_pitch.get("alter")
        note_pitch_value = pitch2int(note_pitch_letter, note_octave, alter)
        if note.find("chord") is None:
            deplacement_numLH += 1
            previous_note = get_previous_note_element(xml, note)
            duration = previous_note.find("duration")
            if duration is not None:
                gap_duration = int(duration.text)
            else:
                gap_duration = 0
            while previous_note.find("rest") is not None:
                p_note = get_previous_note_element(xml, previous_note)
                if p_note != previous_note:
                    previous_note = p_note
                    gap_duration += int(previous_note.find("duration").text)
                else:
                    break
            while previous_note.find("chord") is not None:
                p_note = get_previous_note_element(xml, previous_note)
                if p_note != previous_note:
                    previous_note = p_note
                else:
                    break
            previous_note_pitch = previous_note.find("pitch")
            previous_note_pitch_letter = pitch.get("step")
            previous_note_octave = pitch.get("octave")
            previous_notealter = pitch.get("alter")
            previous_note_pitch_value = pitch2int(previous_note_pitch_letter, previous_note_octave, previous_notealter)
        current_ecart = abs(note_pitch_value - previous_note_pitch_value)
        measure_temp = get_measure_number(xml, note)
        if measure_temp != measure:
            note_num = 1
            measure = measure_temp
        if current_ecart > 12:
            if gap_duration <= base_duration * quickest_value / beat_type * 2:
                diff_deplacementsLH.append([measure, note_num, current_ecart])
        if note.find("accidental") is not None:
            accidental_notesLH.append([measure, note_num, note.find("accidental")])

        if len(note.xpath("time-modification")) != 0:
            time_modificationsLH.append(measure)
        if k < len(notesLH) - 1:
            if note.find("chord") is not None or ((note.find("chord") is None) and notesLH[k+1].find("chord") is not None):
                accord = True
                if note.find("chord") is None:
                    num_chordLH += 1
                    chord_base_value = note_pitch_value
                if note_pitch_value == (chord_base_value + 12):
                    num_octavesLH += 1
            else:
                note_num += 1
    

    if len(diff_deplacementsLH) > 0:
        max_ecart_gauche = diff_deplacementsLH[0]
        for k, v in enumerate(diff_deplacementsLH):
            current_dep = v
            if current_dep[2] > max_ecart_droite[2]:
                max_ecart_gauche = current_dep
        max_intervalLH = max_ecart_gauche[0]
    else:
        max_ecart_gauche = 0
        max_intervalLH = 0
    displacementsLH = len(diff_deplacementsLH) / deplacement_numLH * 100

    polyrhythm = []

    for k, v in enumerate(time_modifications):
        j = 0
        found = False
        while j < len(time_modificationsLH) and not found:
            compare = False
            if time_modificationsLH[j] is not None and v is not None:
                compare = time_modificationsLH[j] < v
            if compare:
                if time_modificationsLH[j] == v:
                    found = True
            j += 1
        if found:
            if len(polyrhythm) == 0:
                polyrhythm.append(v)
            elif v != polyrhythm[-1]:
                polyrhythm.append(v)
    if deplacement_num != 0:
        chord_ratioRH = num_chordRH / deplacement_num * 100
    else:
        chord_ratioRH = 0
    if deplacement_numLH != 0:
        chord_ratioLH = num_chordLH / deplacement_numLH * 100
    else:
        chord_ratioLH = 0
    if num_chordRH != 0:
        octaves_ratioRH = num_octavesRH / num_chordRH * 100
    else:
        octaves_ratioRH = 0
    if num_chordLH != 0:
        octaves_ratioLH = num_octavesLH / num_chordLH * 100
    else:
        octaves_ratioLH = 0

    accidental_ratioRH = len(accidental_notes) / note_counterRH * 100

    accidental_ratioLH = len(accidental_notesLH) / note_counterLH * 100
    
    polyrhythm_ratio = len(polyrhythm) / measure_len * 100

    speed_record = float(tempo) * quickest_value
    speed_result = evaluate_difficulty(Criteria.Speed, rapidite, None)
    displacement_result = evaluate_difficulty(Criteria.Displacement, displacementsRH, displacementsLH)
    chord_result = evaluate_difficulty(Criteria.Chord, chord_ratioRH, chord_ratioLH)
    harmony_result = evaluate_difficulty(Criteria.Harmony, accidental_ratioRH, accidental_ratioLH)
    rhythm_result = evaluate_difficulty(Criteria.Rhythm, polyrhythm_ratio, None)
    length_result = evaluate_difficulty(Criteria.Nbpages, measure_len, None)
    tonality_result = evaluate_difficulty(Criteria.Tonality, abs(int(tonality.text)), None)

    moyenne_result = speed_result + displacement_result + chord_result + harmony_result + rhythm_result + length_result + tonality_result
    moyenne_result /= 7

    print(moyenne_result)


def cal_folder(folder):
    file_list = []  # 存储xml文件路径的列表

    for file_name in os.listdir(folder):
        if file_name.endswith(".xml"):
            file_path = os.path.join(folder, file_name)
            file_list.append(file_path)
            print(file_name)
            cal_xml(file_path)
    pass

if "__main__" == __name__:

    # cal_xml("./demo.xml")
    # cal_folder("./demos")
    cal_folder("./failed")

import enum
import math
# import lxml
from lxml import etree

class Criteria(enum.Enum):
    Speed = "speed"
    Displacement = "displacement"
    Chord = "chord"
    Harmony = "harmony"
    Rhythm = "rhythm"
    Nbpages = "nbpages"
    Tonality = "tonality"

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

# semitone2octave 将半音间距转换为八度艰巨
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
        if 0 is not len(tied):
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
    measure_attributes = the_measure.attributes()
    return measure_attributes["number"]

# get_note_pos_in_mes 获取元素在五线谱上的位置
def get_note_pos_in_mes(xml, note):
    staff = note.staff
    the_measure = get_measure(xml, note)
    the_note = the_measure.xpath(f"./note[staff={staff}]")
    pos = 0
    found = False
    for i in len(the_note):
        if the_note[i] == note:
            found = True
            pos = i
            break
    if found:
        return pos
    else:
        return None

# get_previous_note_element 返回上一个音符，如果不存在则返回当前元素
def get_previous_note_element(xml, note):
    previous_note_prov = note
    pos = get_note_pos_in_mes(xml, note)
    staff = note.staff
    if None is not pos:
        if 1 == pos:
            mes = get_measure_number(xml, note)
            if mes > 1:
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
                previous_note_prov = the_notes_prov[pos-2]
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
    data = None
    with open(path) as f:
        data = f.read()
    # print(type(data)) # str
    return etree.XML(data)

if "__main__" == __name__:
    xml = read_xml("./demo.xml")

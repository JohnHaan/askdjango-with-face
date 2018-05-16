import cognitive_face as CF


def photo_identify(group, photo_file, max_candidates_return=1):
    face_list = CF.face.detect(photo_file)
    face_dict = {
        result_per_face.pop('faceId'): result_per_face
        for result_per_face in face_list }

    if face_dict:
        face_id_list = tuple(face_dict.keys())
        res = CF.face.identify(face_id_list, group.name, max_candidates_return=max_candidates_return)
        for result_per_face in res:
            face_dict[result_per_face['faceId']]['candidates'] = result_per_face['candidates']

    return face_dict


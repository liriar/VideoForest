import pickle
import random
import json

with open("""./tree/new_set/Archery/v_6yTlpxLamho/frame_visual_features.pkl""", 'rb') as f:
        tree = pickle.load(f)
# print(type(tree))
        print(tree)


for key in tree.keys():
        print(key)
# print(f"person_id:{tree['person_id']}\ntime:{tree['time']}\ncaption:{tree['caption']}\n")
#         print(f"{key}:\nperson_id:{tree[key]['person_id']}\ntime:{tree[key]['time']}\ncaption:{tree[key]['caption']}\n")
# print(type(tree["sub_segments"][0]))

# for i in range(len(tree["sub_segments"])):
        # if(i>=20):
        #         break
        # x = tree["sub_segments"][i]
        # print(f"i={i}\nperson_id:{x['person_id']}\ntime:{x['time']}\ncaption:{x['caption']}\n")

        # print(f"i={i}\nperson_id:{x['person_id']}\ntime:{x['time']}\n\n")
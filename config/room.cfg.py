
import json
room_limits = {
				#Type,Start,max,step
		"0"	: [2,50,2], #easy
		"1": [50,1000,50], #normal
		"2": [1000,100000,1000] #advance
}

if __name__ =="__main__":
	with open('room.json',"w") as f:
		f.write(json.dumps(room_limits))


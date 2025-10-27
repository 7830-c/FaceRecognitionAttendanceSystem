from db_util_new import *

init_db()


#relative_path = os.path.join("Data", "StudentImages", f"{idNo}_{safe_name}.png")

for i in fetchStudents():
    id=i[0]
    file_name=i[3].split("/")
    print(str(id)+" : "+str(file_name))
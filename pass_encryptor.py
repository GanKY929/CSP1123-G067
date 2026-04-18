def get_CipheredPassword(ori_password: str) -> str:
    if(ori_password == None):
        print("You did not enter anything.")
        return

    if len(ori_password) > 13:
        print("Password is too long.")
        return 

    special_key = "SalT-Is-way-too-SAlty"
    ori_password_with_key = ori_password + special_key 
    ori_password_with_key_length: int = len(ori_password_with_key)

    list_ciphered_password: str = []

    for i in range(0, ori_password_with_key_length, 2):
        if i == ori_password_with_key_length-1:
            break

        list_ciphered_password.append(str(ori_password_with_key[i])) 
        list_ciphered_password.append("7%6*")
        list_ciphered_password.append(str(ori_password_with_key[i+1]))
        list_ciphered_password.append("$5#6")

    if ori_password_with_key_length % 2 != 0:
        list_ciphered_password.append(str(ori_password_with_key[ori_password_with_key_length-1]))
        list_ciphered_password.append("7%6*")

    password = "".join(list_ciphered_password)
    final_password = password.replace("a", "1").replace("b", "1").replace("c", "1").replace("d", "1").replace("w", "0").replace("x", "0").replace("y", "0").replace("z", "0").replace("-", "*")

    return final_password    
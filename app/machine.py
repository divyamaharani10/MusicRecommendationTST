import operator
import random
import babygenerator
def initial(jenis_kelamin, jumlah_huruf_minimal, jumlah_huruf_maksimal, jumlah_nama):
    
    data = []
    if jenis_kelamin.upper() == str('L'):
        f = open("lakilaki.txt", "r")
        data = f.read().lower().split('\n')
        other_f = open("perempuan.txt", "r")
        other_data = other_f.read().lower().split('\n')
        f.close(); other_f.close()
    else: 
        f = open("perempuan.txt", "r")
        data = f.read().lower().split('\n')
        other_f = open("lakilaki.txt", "r")
        other_data = other_f.read().lower().split('\n')
        f.close(); other_f.close()

    my_dict = getnamaDict(data)
    final_nama = []
    while len(final_nama) < jumlah_nama:
        nama = generatenama(my_dict)
        if len(nama) >= jumlah_huruf_minimal and len(nama) <= jumlah_huruf_maksimal and nama not in final_nama and nama.title() not in data and nama.title() not in other_data:
            final_nama.append(nama)
    # printLayar(jumlah_nama, jenis_kelamin, final_nama)
    return final_nama
    
        
# def printLayar(number, jenis_kelamin, list_nama,):
#     if (jenis_kelamin.upper() == str("L")): jenis_kelamin = "laki - laki"
#     else: jenis_kelamin = "perempuan"
#     print ("Berikut adalah " + str(number) + " nama calon bayi " + str(jenis_kelamin) + " Anda: ")
#     for nama in list_nama:
#         print(nama.title())

# building data for Markov model 
def getnamaDict(nama):
    # ease the parsing of data
    list_nama = []
    for nama in nama:
        if (nama != ""):
            list_nama.append("__" + nama + "__")
    #
    dict_of_nama = {}
    for nama in list_nama:                                     
        for i in range(len(nama)-3):
            kombinasi = nama[i:i+2]                               
            if kombinasi not in dict_of_nama:                   
                dict_of_nama[kombinasi] = []                   
            dict_of_nama[kombinasi].append(nama[i+2])          
    return dict_of_nama                                           


# generating new nama
def generatenama(dict_of_nama):
    kombinasi = "__"
    next_letter = ""
    hasil = ""
    while True: 
        number_of_letters = len(dict_of_nama[kombinasi])       
        index = random.randint(0,number_of_letters - 1)            
        next_letter = dict_of_nama[kombinasi][index]             
        if next_letter == "_":                                  
            break                                                
        else:
            hasil = hasil + next_letter
            kombinasi = kombinasi[1] + next_letter
    return hasil

# NamaGenerator()

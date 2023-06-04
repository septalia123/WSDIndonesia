from kbbi import TidakDitemukan
from kbbi import AutentikasiKBBI
from kbbi import KBBI
import streamlit as st
import nltk
import re
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
factory = StemmerFactory()
stemmer = factory.create_stemmer()
stopWords = stopwords.words('Indonesian')

# ===================================================================== KBBI =============================================
auth = AutentikasiKBBI("septaliaputri77@gmail.com", "septalia123")

# ====================================================================== TITTLE===========================================
st.title("Sistem Word Sense Disambiguation Bahasa Indonesia")

# ============================================================ MENAMPILKAN INPUT DAN BUTTON ===============================
kalimat = st.text_input("Inputkan Kalimat: ")
proses = st.button("Proses Kalimat")

# ====================================================================== PREPROCESSING DATA ===============================
def preproces(kalimat):
    lower = kalimat.lower()

    tokenisasi = word_tokenize(lower)
        
    #proses Stopword Removal
    stopWords.remove('asal')
    stopWords.remove('atas')
    stopWords.remove('besar')
    stopWords.remove('dini')
    stopWords.remove('diri')
    stopWords.remove('dua')
    stopWords.remove('empat')
    stopWords.remove('luar')
    stopWords.remove('masih')
    stopWords.remove('naik')
    stopWords.remove('panjang')
    stopWords.remove('semata')
    stopWords.remove('waktu')
    stopWordsd = set(stopWords)
    word_tokens_no_stopwords = [w for w in tokenisasi if not w in stopWordsd]
    
    #menghapus karakter dan menggantinya dengan spasi/karakter kosong
    special_char = "+=`@_!#$%^&*()<>?/\|}{~:;.[],1234567890‘’'" + '"“”●'
    cleaning = [''.join(x for x in string if not x in special_char) for string in word_tokens_no_stopwords]
    while '' in cleaning:
        cleaning.remove('')
    return cleaning

cleaning = preproces(kalimat)

# ====================================================================== PEMBENTUKAN N-DATA ===============================
def ngram(data, n):
    gram = []
    for ng in cleaning:
        temp=zip(*[cleaning[ng:] for ng in range(0,n)])
        gram=[' '.join(n) for n in temp]
    return gram

unigram = ngram(cleaning, 1)
bigram = ngram(cleaning, 2)
trigram = ngram(cleaning, 3)

# ====================================================================== PENCARIAN KATA BERMAKNA ===============================
def NewKata(kata):
    new_kata = []
    for nkata in kata:
        try:
            cari = KBBI(nkata, auth)
            new_kata.append(nkata)
        except TidakDitemukan:
            xnkata = stemmer.stem(nkata)
            try:
                cari = KBBI(xnkata, auth)
                new_kata.append(xnkata)
            except TidakDitemukan:
                del nkata
    return new_kata

new_unigram = NewKata(unigram)
new_bigram = NewKata(bigram)
new_trigram = NewKata(trigram)

# ====================================================================== MENGAMBIL MAKNA KATA ===============================
def makna(kata):
    makna = []
    for nkata in kata:
        makna_kata = []
        cari = KBBI(nkata, auth)
        dmakna = cari.__str__(contoh=True, terkait=False, fitur_pengguna=False)

        #proses memberi index tiap makna dan menghapus makna pertama
        stc = sent_tokenize(dmakna)
        if len(stc)>1:
            del stc[0]
        for u in range (len(stc)):
            #mengubah -- menjadi kata yang dicari
            if '--' in stc[u]:
                stc[u] = stc[u].replace('--', nkata) 
                    
            #menghapus tanda baca, angka, dan space pada makna
            del_angka_makna = re.sub(r"\d+", '', stc[u])
            if "\n" in del_angka_makna:
                del_angka_makna = del_angka_makna.replace('\n' and '\nn', " ")
                del_angka_makna = del_angka_makna.replace('.', " ")
            del_spc_makna = del_angka_makna.strip()
            makna_kata.append(del_spc_makna)
        makna.append(makna_kata)   
    return makna

makna_unigram = makna(new_unigram)
makna_bigram = makna(new_bigram)
makna_trigram = makna(new_trigram)

# ====================================================================== SELEKSI DATA N-GRAM ===============================
def skata(dkata):
    seleksi = []
    for z in new_unigram:
        seleksi.append(z)
    if len(new_trigram) == 0:
        for i in new_bigram:
            pecah = word_tokenize(i)
            for j in new_unigram:
                if j == pecah[0]:
                    idx = seleksi.index(pecah[0])
                    seleksi[idx] = i
                    del seleksi[idx+1]
                    break
                elif j == pecah[1]:
                    idx = seleksi.index(pecah[1])
                    seleksi[idx] = i
                    del seleksi[idx-1]
                    break
    else:
        for i in new_trigram:
            pecah = word_tokenize(i)
            for j in new_unigram:
                if j == pecah[0]:
                    idx = seleksi.index(pecah[0])
                    seleksi[idx] = i
                    del seleksi[idx+1]
                    del seleksi[idx+1]
                    break
                elif j == pecah[1]:
                    idx = seleksi.index(pecah[1])
                    seleksi[idx] = i
                    del seleksi[idx-1]
                    del seleksi[idx]
                    break
                elif j == pecah[2]:
                    idx = seleksi.index(pecah[2])
                    seleksi[idx] = i
                    del seleksi[idx-1]
                    del seleksi[idx-1]
                    break
    
            for k in new_bigram:
                pecah = word_tokenize(k)
                for j in new_unigram:
                    if j == pecah[0]:
                        idx = seleksi.index(pecah[0])
                        seleksi[idx] = k
                        del seleksi[idx+1]
                    elif j == pecah[1]:
                        idx = seleksi.index(pecah[1])
                        seleksi[idx] = k
                        del seleksi[idx-1]
    return seleksi

seleksi_kata = skata(new_unigram)

# ====================================================================== SELEKSI MAKNA DATA N-GRAM ===============================
def smakna(dmakna):
    seleksi_makna = []
    for j in seleksi_kata:
        if j in new_unigram:
            idx = new_unigram.index(j)
            makna = makna_unigram[idx]
            seleksi_makna.append(makna)
        if j in new_bigram:
            idx = new_bigram.index(j)
            makna = makna_bigram[idx]
            seleksi_makna.append(makna)
        if j in new_trigram:
            idx = new_trigram.index(j)
            makna = makna_trigram[idx]
            seleksi_makna.append(makna)
    return seleksi_makna

seleksi_makna = smakna(seleksi_kata)

# ====================================================================== MENGHITUNG SKOR LESK ===============================
def skor(seleksi_kata):
    count = 0
    skor_makna=[]
    while count != len(seleksi_kata):
        if len(seleksi_makna[count]) == 1:
            skor_makna.append("OK")
        else:
            skor_makna_kata=[]
            for i in range(len(seleksi_makna[count])):
                setmakna = set(word_tokenize(seleksi_makna[count][i]))
                setkalimat = set(word_tokenize(kalimat.lower()))
                irisan = setmakna&setkalimat
                skor_makna_kata.append(len(irisan))
            skor_makna.append(skor_makna_kata)
        count +=1
    return skor_makna
skor_makna = skor(seleksi_kata)

# ====================================================================== MENENTUKAN MAKNA ===============================
def SimplifiedLesk(skor_makna):
    count2 = 0
    makna_pilihan = []
    while count2!= len(skor_makna):
        if skor_makna[count2] != "OK":
            lmax = max(skor_makna[count2])
            idx = skor_makna[count2].index(lmax)
            makna_pilihan.append(seleksi_makna[count2][idx])
        else:
            makna_pilihan.append(seleksi_makna[count2][0])
        count2+=1
    return makna_pilihan
hasil = SimplifiedLesk(skor_makna)


# ===================================================================== Menampilkan Hasil ==================================
if proses:
    c3 = 0
    while c3 != len(seleksi_kata):
        st.warning(f"Kata : {seleksi_kata[c3]}")
        if len(seleksi_makna[c3]) == 1:
            st.write(seleksi_makna[c3][0])
        else:
            for i in range(len(seleksi_makna[c3])):
                if seleksi_makna[c3][i] == hasil[c3]:
                    st.success(
                        f"{hasil[c3]} (Skor Makna : {skor_makna[c3][i]})")
                else:
                    st.write(
                        i+1, seleksi_makna[c3][i], "(Skor Makna : ", skor_makna[c3][i], ")")
        c3 += 1
    #st.write("Hasil CF = ", cf)
    #st.write("Hasil Preprocessing = ", cleaning)
    #st.write("Data Unigram = ", unigram)
    #st.write("Data Bigram = ", bigram)
    #st.write("Data Trigram = ", trigram)
    #st.write("Data Unigram New = ", new_unigram)
    #st.write("Data Bigram New = ", new_bigram)
    #st.write("Data Trigram New = ", new_trigram)
    #st.write("Makna Uni = ", makna_unigram)
    #st.write("Makna Big = ", makna_bigram)
    #st.write("Makna Tri = ", makna_trigram)
    #st.write("Seleksi Kata = ", seleksi)
    #st.write("Seleksi Makna = ", seleksi_makna)
    #st.write("Seleksi Makna = ", skor_makna)
    #st.write("Makna pilihan = ", makna_pilihan)

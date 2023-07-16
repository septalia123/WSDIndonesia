from kbbi import TidakDitemukan
from kbbi import AutentikasiKBBI
from kbbi import KBBI
import streamlit as st
import nltk
import re
#from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
factory = StemmerFactory()
stemmer = factory.create_stemmer()
#stopWords = stopwords.words('Indonesian')

# ===================================================================== KBBI =============================================
auth = AutentikasiKBBI("liaseptaliaa@gmail.com", "lialia123")

# ====================================================================== TITTLE===========================================
st.title("Sistem Word Sense Disambiguation Bahasa Indonesia")

# ============================================================ MENAMPILKAN INPUT DAN BUTTON ===============================
kalimat = st.text_input("Inputkan Kalimat: ")
proses = st.button("Proses Kalimat")

# ====================================================================== PREPROCESSING DATA ===============================


def preproces(kalimat):
    lower = kalimat.lower()

    tokenisasi = word_tokenize(lower)

    # proses Stopword Removal
    #stopWords.remove('asal')
    #stopWords.remove('atas')
    #stopWords.remove('besar')
    #stopWords.remove('dini')
    #stopWords.remove('diri')
    #stopWords.remove('dua')
    #stopWords.remove('empat')
    #stopWords.remove('luar')
    #stopWords.remove('masih')
    #stopWords.remove('naik')
    #stopWords.remove('panjang')
    #stopWords.remove('semata')
    #stopWords.remove('waktu')
    #stopWords.remove('tahun')
    #stopWordsd = set(stopWords)
    #word_tokens_no_stopwords = [w for w in tokenisasi if not w in stopWordsd]

    # menghapus karakter dan menggantinya dengan spasi/karakter kosong
    special_char = "+=`@_!#$%^&*()<>?/\|}{~:;.[],1234567890‘’'" + '"“”●'
    cleaning = [''.join(x for x in string if not x in special_char)
                for string in tokenisasi]
    while '' in cleaning:
        cleaning.remove('')
    return cleaning


cleaning = preproces(kalimat)

# ====================================================================== PEMBENTUKAN N-DATA ===============================


def ngram(data, n):
    gram = []
    for ng in cleaning:
        temp = zip(*[cleaning[ng:] for ng in range(0, n)])
        gram = [' '.join(n) for n in temp]
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
        split_makna1 = dmakna.split('\n\n')
        stc = []
        if len(split_makna1)==1:
            split_makna2 = split_makna1[0].split('\n')
            for i in range(len(split_makna2)):
                if i!=0 and 'bentuk tidak baku' not in split_makna2[i]:
                    stc.append(split_makna2[i])
        else:
            for i in split_makna1:
                split_makna2 = i.split('\n')
                for k in range(len(split_makna2)):
                    if k != 0 and 'bentuk tidak baku' not in split_makna2[k]:
                        stc.append(split_makna2[k])
        
        #mengubah tanda menjadi kata
        for u in range (len(stc)):
            #mengubah -- menjadi kata yang dicari
            if '--' in stc[u]:
                stc[u] = stc[u].replace('--', nkata) 
            elif '~' in stc[u]:
                stc[u] = stc[u].replace('~', nkata) 
                    
            #menghapus tanda baca, angka, dan space pada makna
            del_angka_makna = re.sub(r"\d+", '', stc[u])
            del_tdb_makna = del_angka_makna.replace('.', " ")
            del_spc_makna = del_tdb_makna.strip()
            makna_kata.append(del_spc_makna)
        makna.append(makna_kata)
    return makna

makna_unigram = makna(new_unigram)
makna_bigram = makna(new_bigram)
makna_trigram = makna(new_trigram)

# ====================================================================== SELEKSI DATA N-GRAM ===============================

def skata(dkata):
    seleksi = []
    if len(new_trigram) == 0:
        n = 0
        for db in new_bigram:
            pecah = word_tokenize(db)
            while n != len(new_unigram):
                if new_unigram[n] in db:
                    if new_unigram[n] == pecah[0]:
                        seleksi.append(db)
                        n = new_unigram.index(pecah[0])+2
                        break
                    else:
                        seleksi.append(db)
                        del seleksi[-2]
                        n = new_unigram.index(pecah[1])+1
                        break
                else:
                    seleksi.append(new_unigram[n])
                    n += 1

        if len(seleksi) != (len(new_unigram)-len(new_bigram)):
            tambah_kata = len(seleksi)+len(new_bigram)
            for k in range(tambah_kata, len(new_unigram)):
                seleksi.append(new_unigram[k])
    else:
        n = 0
        for dt in new_trigram:
            pecah = word_tokenize(dt)
            while n != len(new_unigram):
                if new_unigram[n] in dt:
                    if new_unigram[n] == pecah[0]:
                        seleksi.append(dt)
                        n = new_unigram.index(pecah[0])+3
                        break
                    elif new_unigram[n] == pecah[1]:
                        seleksi.append(dt)
                        n = new_unigram.index(pecah[1])+2
                        del seleksi[-2]
                        break
                    else:
                        seleksi.append(dt)
                        n = new_unigram.index(pecah[2])+1
                        del seleksi[-2]
                        del seleksi[-2]
                        break
                else:
                    seleksi.append(new_unigram[n])
                    n += 1

        if len(seleksi) != (len(new_unigram)-len(new_trigram)):
            tambah_kata = len(seleksi)+len(new_trigram)+(1*len(new_trigram))
            for k in range(tambah_kata, len(new_unigram)):
                seleksi.append(new_unigram[k])

        if len(new_bigram) != 0:
            for db in new_bigram:
                pecah = word_tokenize(db)
                for i in seleksi:
                    if i == pecah[0]:
                        idx = seleksi.index(pecah[0])
                        seleksi[idx] = db
                        del seleksi[idx+1]
                    elif i == pecah[1]:
                        idx = seleksi.index(pecah[1])
                        seleksi[idx] = db
                        del seleksi[idx-1]
    return seleksi


seleksi_kata = skata(new_trigram)

# ====================================================================== SELEKSI MAKNA N-GRAM ===============================
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
    skor_makna = []
    while count != len(seleksi_kata):
        if len(seleksi_makna[count]) == 1:
            skor_makna.append("OK")
        else:
            skor_makna_kata = []
            for i in range(len(seleksi_makna[count])):
                setmakna = set(word_tokenize(seleksi_makna[count][i]))
                setkalimat = set(word_tokenize(kalimat.lower()))
                irisan = setmakna & setkalimat
                skor_makna_kata.append(len(irisan))
            skor_makna.append(skor_makna_kata)
        count += 1
    return skor_makna


skor_makna = skor(seleksi_kata)

# ====================================================================== MENENTUKAN MAKNA ===============================


def SimplifiedLesk(skor_makna):
    count2 = 0
    makna_pilihan = []
    while count2 != len(skor_makna):
        if skor_makna[count2] != "OK":
            lmax = max(skor_makna[count2])
            idx = skor_makna[count2].index(lmax)
            makna_pilihan.append(seleksi_makna[count2][idx])
        else:
            makna_pilihan.append(seleksi_makna[count2][0])
        count2 += 1
    return makna_pilihan


hasil = SimplifiedLesk(skor_makna)


# ===================================================================== Menampilkan Hasil ==================================
if proses:
    for kata in range(len(seleksi_kata)):
        st.warning(f"Kata : {seleksi_kata[kata]}")
        if skor_makna[kata] == 'OK':
            st.write(seleksi_makna[kata][0])
        else:
            for i in range(len(skor_makna[kata])):
                if seleksi_makna[kata][i] == hasil[kata]:
                    st.success(
                        f"{i+1}. {seleksi_makna[kata][i]} (Skor Makna : {skor_makna[kata][i]})")
                else:
                    st.write(
                        i+1,".", seleksi_makna[kata][i], "(Skor Makna : ", skor_makna[kata][i], ")")

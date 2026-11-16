package main

import (
	"flag"
	"os"
	"io"
	"fmt"
	"time"
	"encoding/binary"
	"crypto/hmac"
	"crypto/sha1"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"github.com/skip2/go-qrcode"
)

func main() {
	// Clé AES-256 (doit faire exactement 32 octets)
	cryptingKey := []byte("zTQQiP4oxIIa7Q0cS1M10vkvRCwO6eie")

	g_file := flag.String("g", "", "File containing the key which will be copied and stored in an encrypted file")
	k_file := flag.String("k", "", "File used to generate the OTP (Ex: ft_otp.key)")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [OPTION] [ARG]\n\nOptions :\n", os.Args[0])
		flag.PrintDefaults()
	}

	flag.Parse()

	if *g_file == "" && *k_file == "" {
		flag.Usage()
		os.Exit(1)
	}

	if *g_file != "" {
		if err := EncryptFile(*g_file, cryptingKey); err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		fmt.Println("Crypted file created")
	}
	if *k_file != "" {
		uncryptedKey, err := DecryptFile(*k_file, cryptingKey)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		// unix time (seconds since 1st jan 1970)
		now := time.Now()
		// diviser par 30 pour que la valeur final change toutes les 30 secondes
		counter := now.Unix() / 30 

		// alloc tableau de 8 octets
		buf := make([]byte, 8)

		// litle Endian -> big Endian dans le tableau de 8 octets
		binary.BigEndian.PutUint64(buf, uint64(counter))
		// prepa de la cle et de l'algo de hashage
		h := hmac.New(sha1.New, []byte(uncryptedKey))
		// passer le buffer qui contient le temp actuel a h
		h.Write(buf)
		// on calcul et recuper le resultat dans result (20 cases de tableau)
		result := h.Sum(nil)

		// masque hexa (0x0F) = 15, ET logique pour avoir un offset entre 0 et 15 en utilisant la derniere case du tableau result
		offset := result[19] & 0x0F
		// litle Endian -> big Endian de l'offset a offset + 4 du tableau, BigEndian permet aussi de transformer 4 case de tableau en un seul int
		binCode := binary.BigEndian.Uint32(result[offset : offset+4])
		// le masque 0x7FFFFFFF efface le bit de poid fort, force une valeur positive 
		binCode = binCode & 0x7FFFFFFF
		// garder les 5 dernier chiffres seulement
		otp := binCode % 1000000

		fmt.Printf("Code TOTP : %06d\n", otp)
	}
}

func CreateQRCode(content string) {
	// Nom du fichier de sortie
    filePath := "qrcode.png"

    // Taille de l'image en pixels (ex: 256x256)
    size := 256

    // Génération du QR code et sauvegarde en PNG
    err := qrcode.WriteFile(content, qrcode.Medium, size, filePath)
    if err != nil {
        fmt.Errorf("Error while generating QR code : %v", err)
    }
}

func IsValidHexFile(fileContent string) (bool) {
	if len(fileContent) < 64 {
		return false
	}

	for _, b := range fileContent {
		isDigit := b >= '0' && b <= '9'
		isLower := b >= 'a' && b <= 'f'
		isUpper := b >= 'A' && b <= 'F'
		if !isDigit && !isLower && !isUpper {
			return false
		}
	}
	return true
}

func EncryptFile(srcPath string, key []byte) error {
	plaintext, err := os.ReadFile(srcPath)
	if err != nil {
		return err
	}

	if IsValidHexFile(string(plaintext)) == false {
		return fmt.Errorf("Wrong content format")
	}

	// initialise le moteur AES avec la clé secrète 32o max, a ce stade on ne peut chiffrer qu'un bloc de la taille de key maximum (32octets)
	block, err := aes.NewCipher(key)
	if err != nil {
		return err
	}

	// Active le mode GCM pour sécuriser et chiffrer tout un fichier au lieu de 32o
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return err
	}

	// alloc d'un tableau de la taille requise pour nonce
	nonce := make([]byte, gcm.NonceSize())
	
	// remplit le tableau nonce au complet avec des valeur random (/dev/urandom sur unix)
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		return err
	}

	// Chiffre les données, ajoute la signature, et préfixe le tout avec le Nonce
	ciphertext := gcm.Seal(nonce, nonce, plaintext, nil)

	// résultat dans ft_otp.key avec les permissions standard
	CreateQRCode(string(ciphertext))
	return os.WriteFile("ft_otp.key", ciphertext, 0644)
}

func DecryptFile(srcPath string, key []byte) (string, error) {
	ciphertext, err := os.ReadFile(srcPath)
	if err != nil {
		return "", err
	}

	block, err := aes.NewCipher(key)
	if err != nil {
		return "", err
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", err
	}

	nonceSize := gcm.NonceSize()
	if len(ciphertext) < nonceSize {
		return "", fmt.Errorf("file to short")
	}

	// Coupe le fichier en deux virtuellement (Nonce d'un côté, Données de l'autre)
	nonce, cipherContent := ciphertext[:nonceSize], ciphertext[nonceSize:]

	// Vérifie la signature et déchiffre les données
	plaintext, err := gcm.Open(nil, nonce, cipherContent, nil)
	if err != nil {
		return "", fmt.Errorf("Decryption failed : %w", err)
	}

	if IsValidHexFile(string(plaintext)) == false {
		return "", fmt.Errorf("Wrong content format")
	}

	return string(plaintext), err
}

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
		// T is (unix time (seconds since 1st jan 1970) / 30)
		now := time.Now()
		// hmac = HMAC-SHA-1(K, T)
		counter := now.Unix() / 30
		buf := make([]byte, 8)
		binary.BigEndian.PutUint64(buf, uint64(counter))
		h := hmac.New(sha1.New, []byte(uncryptedKey))
		h.Write(buf)
		result := h.Sum(nil)
		fmt.Println(result)
		// TODO return table 
		// [70 112 181 45 86 59 190 246 66 167 116 179 23 246 58 229 247 237 112 204]

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

	// Prépare le moteur AES avec la clé secrète 32o max
	block, err := aes.NewCipher(key)
	if err != nil {
		return err
	}

	// Active le mode GCM pour sécuriser et chiffrer tout un fichier
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return err
	}

	// Crée un espace vide de 12 octets pour le "grain de sel" (Nonce)
	nonce := make([]byte, gcm.NonceSize())
	
	// Remplit cet espace avec de l'aléatoire sécurisé
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		return err
	}

	// Chiffre les données, ajoute la signature, et préfixe le tout avec le Nonce
	ciphertext := gcm.Seal(nonce, nonce, plaintext, nil)

	// Écrit le résultat final dans un nouveau fichier avec les permissions standard
	return os.WriteFile("ft_otp.key", ciphertext, 0644)
}

func DecryptFile(srcPath string, key []byte) (string, error) {
	ciphertext, err := os.ReadFile(srcPath)
	if err != nil {
		return "", err
	}

	// Recrée le moteur AES avec la même clé
	block, err := aes.NewCipher(key)
	if err != nil {
		return "", err
	}

	// Réactive le mode GCM
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", err
	}

	// Récupère la taille attendue du Nonce (12 octets)
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

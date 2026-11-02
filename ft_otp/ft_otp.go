package main

import (
	"flag"
	"os"
	"io"
	"fmt"
	// "time"
)

func main()  {
	// 1. Définition des options
	// Syntaxe : flag.Type("nom_option", valeur_par_defaut, "description")
	// Ces fonctions renvoient des POINTEURS vers les valeurs
	g_file := flag.String("g", "", "Key file encryption")
	k_file := flag.String("k", "", "File used to generate the OTP")

	// Personnalisation du message d'aide (Optionnel)
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [OPTION] [ARG]\n\nOptions :\n", os.Args[0])
		flag.PrintDefaults()
	}

	flag.Parse()

	if *g_file == "" {
		flag.Usage()
	}



	// manage the args -g ... 
		// if file exist
		// copy file content
		// if hexa and if len >= 64char
			// create file ft_otp.key encrypted
			// paste key
	// AND -k ...
		// if file exist
		// copy file content in K
	// K = secret key stored previously in argv[2]
	// T is (unix time (seconds since 1st jan 1970) / 30)
	// hmac = HMAC-SHA-1(K, T)
	// print hmac
}
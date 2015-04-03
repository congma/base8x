# base8x

## SYNOPSIS

`base8x` -- Base-(85 ~ 95) binary/ASCII conversion.

Encodes binary data 4 bytes a time into a string of maximal length 5, using
only ASCII printable characters.  The alphabet can be specified by the user.
The inverse operation (decoding) can also be performed.


## USAGE

See docstring for the `Base8xCodec` class.


## EXAMPLE

The example script `example_wpskg.py` generates random secret keys for
WordPress's `wp-config.php` file, just like WP's online key generation service
at https://api.wordpress.org/secret-key/1.1/salt/  Binary data from the random
source `/dev/urandom` is converted into strings suitable for use as PHP
literal.

The output should look like the following:

```php
define('AUTH_KEY',         'TRb]|u{xmvW7,02tiDA@j|{iSMMqxbu~k #R|H-UmZJXeJSU:9');
define('SECURE_AUTH_KEY',  '5KYxKE`{|}QWdV6824j[eGf7sBh(S+72;Pdp@-kK1Dy:^PlsbT');
define('LOGGED_IN_KEY',    'a@L(:kQ<c(vGfQ4uN4dSF:K];5Zv.SFR+JKUj1T@J?qfJr@hz?');
define('NONCE_KEY',        'i@WA`bw=m[z#+N9FDW}1gVmv/Wb~3{S^T,2ctv7Tya]QPw_w>b');
define('AUTH_SALT',        'N>#Q&nYIBkn/?to0#N#/O|N:P0h;ycAWc`(1~twk4{P7bc@1,Z');
define('SECURE_AUTH_SALT', 'Nm0r2DC~vbhoBzx7uT{vwAr9lNd02}Rc~xVf968gC^S`#4acPF');
define('LOGGED_IN_SALT',   'Pp9sSh#%R)pTk<HS)qR@2qsy+dW]@fl!s@]9kq!byTrQQoij6y');
define('NONCE_SALT',       'qAIqsm4-&SU4-BP8CP=UI6YXeTn,c7Bx4NRl`Msib|4 qt:A]D');
```

*NOTE:*  Please don't copy the above example output into your `wp-config.php`
file.


## COPYRIGHT

Copyright © 2015 Cong Ma.  License BSD: See the COPYING file.

This is free software: you are free to change and redistribute it.  
There is NO WARRANTY, to the extent permitted by law.


## AVAILABILITY

Available from [https://github.com/congma/base8x][githubrepo].


[githubrepo]: https://github.com/congma/base8x "GitHub repository page for base8x"

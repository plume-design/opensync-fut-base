# Watchdog Proxy Daemon - WPD test suite

The `Watchdog Proxy Daemon - WPD` provides a proxy between a hardware watchdog timer and `OpenSync`. It stimulates the
hardware watchdog timer while `OpenSync` remains sufficiently responsive. In case of system anomalies, if the `WPD`
fails to refresh and the hardware watchdog timer expires, the hardware watchdog intervenes by resetting the system.
`OpenSync` is responsible for providing the daemon with information affirming that it is functioning correctly,
prompting the daemon to continue stimulating the hardware watchdog timer.

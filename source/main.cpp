#include <emscripten/console.h>

int main(int argc, char* argv[]) {
	emscripten_console_log(WGK_PROJECT_NAME);

	return 0;
}

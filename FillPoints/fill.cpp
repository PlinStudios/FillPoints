#include <cstdint>
#include <cstring>
#include <queue>
#include <unordered_set>
#include <array>

inline int index(int x, int y, int w) {
    return y * w + x;
}

extern "C" __declspec(dllexport)
void expand_color_to_line(const uint8_t* color_data, const uint8_t* line_data, uint8_t* out_data, int w, int h, uint8_t line_opacity) {
    int size = w * h * 4;
    std::memcpy(out_data, color_data, size);

    using Pixel = std::tuple<int, int, std::array<uint8_t,4>>;
    std::queue<Pixel> queue;
    std::vector<bool> visited(w * h, false);

    //init queue
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            int idx = 4 * index(x, y, w);
            if (out_data[idx + 3] == 255) {
                std::array<uint8_t,4> col = {
                    out_data[idx + 0],
                    out_data[idx + 1],
                    out_data[idx + 2],
                    out_data[idx + 3]
                };
                queue.emplace(x, y, col);
                visited[index(x, y, w)] = true;
            }
        }
    }

    const int dx[4] = { -1, 1, 0, 0 };
    const int dy[4] = { 0, 0, -1, 1 };

    //BFS
    while (!queue.empty()) {
        auto [x, y, col] = queue.front();
        queue.pop();

        for (int i = 0; i < 4; ++i) {
            int nx = x + dx[i];
            int ny = y + dy[i];

            if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
            int nidx = index(nx, ny, w);
            if (visited[nidx]) continue;

            int line_alpha = line_data[4 * nidx + 3];
            int dst_alpha = out_data[4 * nidx + 3];

            if (line_alpha < line_opacity && dst_alpha != 255) {
                int offset = 4 * nidx;
                for (int c = 0; c < 4; ++c)
                    out_data[offset + c] = col[c];

                visited[nidx] = true;
                queue.emplace(nx, ny, col);
            }
        }
    }
}

extern "C" __declspec(dllexport)
void expand_color_free(uint8_t* out_data, int w, int h, int expansion) {
    int size = w * h * 4;

    using Pixel = std::tuple<int, int, std::array<uint8_t,4>>;
    std::queue<Pixel> queue;
    std::vector<bool> visited(w * h, false);

    //init queue
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            int idx = 4 * index(x, y, w);
            if (out_data[idx + 3] == 255) {
                std::array<uint8_t,4> col = {
                    out_data[idx + 0],
                    out_data[idx + 1],
                    out_data[idx + 2],
                    out_data[idx + 3]
                };
                queue.emplace(x, y, col);
                visited[index(x, y, w)] = true;
            }
        }
    }

    const int dx[4] = { -1, 1, 0, 0 };
    const int dy[4] = { 0, 0, -1, 1 };

    //BFS per levels
    for (int k = 0; k < expansion; k++) {
        size_t current_level_size = queue.size();

        for (size_t i = 0; i < current_level_size; i++) {
            auto [x, y, col] = queue.front();
            queue.pop();

            for (int d = 0; d < 4; d++) {
                int nx = x + dx[d];
                int ny = y + dy[d];

                if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
                int nidx = index(nx, ny, w);
                if (visited[nidx]) continue;

                int offset = 4 * nidx;
                if (out_data[offset + 3] != 255) {
                    for (int c = 0; c < 4; c++)
                        out_data[offset + c] = col[c];

                    visited[nidx] = true;
                    queue.emplace(nx, ny, col);
                }
            }
        }
    }
}

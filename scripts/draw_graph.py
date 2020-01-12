import matplotlib.pyplot as plt

dege_log_data = {'path': r'../checkpoints/log_edge.dat', 'data': 5, 'name': 'precision', 'range': (0.0, 1.0)}


def preprocess(coord_x_list, coord_y_list, multiple):
    multiple = max(int(multiple), 1)
    new_coord_x_list = []
    new_coord_y_list = []

    all_x, all_y, times = 0, 0, 0
    for x, y in zip(coord_x_list, coord_y_list):
        all_x += x
        all_y += y
        times += 1

        if times >= multiple:
            new_coord_x_list.append(all_x / times)
            new_coord_y_list.append(all_y / times)
            all_x, all_y, times = 0, 0, 0

    new_coord_x_list.append(all_x / times)
    new_coord_y_list.append(all_y / times)

    return new_coord_x_list, new_coord_y_list


def read_files(log_data, preprocess):
    with open(log_data['path'], "r") as f:
        datas = f.readlines()
        coord_x_list = []
        coord_y_list = []
        for index, data_str in enumerate(datas):
            data_list = data_str.split(' ')
            coord_x_list.append(index)
            coord_y_list.append(round(float(data_list[log_data['data']]), 3))

        if preprocess:
            coord_x_list, coord_y_list = preprocess(coord_x_list, coord_y_list, 100)
        draw_graph(coord_x_list, coord_y_list, log_data['range'], log_data['name'])


def draw_graph(coord_x_list, coord_y_list, range=(0.0, 1.0), y_name='data'):
    plt.xlabel('time')  # x轴上的名字
    plt.ylabel(y_name)  # y轴上的名字

    plt.ylim(range)

    plt.plot(coord_x_list, coord_y_list, color='orange')
    plt.show()


if __name__ == "__main__":
    read_files(dege_log_data, preprocess)

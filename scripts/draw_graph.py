import matplotlib.pyplot as plt

dege_log_data = {'path': r'../checkpoints/log_edge_inpaint.dat', 'data': 7, 'name': 'psnr', 'range': (15.0, 26.0)}


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


def read_files(log_data):
    coord_x_lists, coord_y_lists = [], []
    with open(log_data['path'], "r") as f:
        datas = f.readlines()
        coord_x_list = []
        coord_y_list = []
        for index, data_str in enumerate(datas):
            data_list = data_str.split(' ')
            coord_x_list.append(index)
            coord_y_list.append(round(float(data_list[log_data['data']]), 3))

        coord_x_list1, coord_y_list1 = preprocess(coord_x_list, coord_y_list, 100)
        coord_x_lists.append(coord_x_list1)
        coord_y_lists.append(coord_y_list1)
        coord_x_list2, coord_y_list2 = preprocess(coord_x_list, coord_y_list, 1000)
        coord_x_lists.append(coord_x_list2)
        coord_y_lists.append(coord_y_list2)
        draw_graph(coord_x_lists, coord_y_lists, log_data['range'])


def draw_graph(coord_x_lists, coord_y_lists, range=(0.0, 1.0), y_name='data'):
    import numpy
    numpy.random.seed(9)

    for index, pack in enumerate(zip(coord_x_lists, coord_y_lists)):
        coord_x_list, coord_y_list = pack

        plt.xlabel('time')  # x轴上的名字
        plt.ylabel(y_name)  # y轴上的名字

        plt.ylim(range)

        r = numpy.random.rand()
        g = numpy.random.rand()
        b = 1 - r
        line_color = (r, g, b)
        plt.plot(coord_x_list, coord_y_list, color=line_color, label=str(index))

    plt.show()

if __name__ == "__main__":
    read_files(dege_log_data)

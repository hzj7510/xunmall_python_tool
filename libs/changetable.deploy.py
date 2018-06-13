#_*_ coding: utf8 _*_

import pymysql
import argparse
import sys

#链接数据库
def connect_database(db='mall'):
    try:
        conn = pymysql.connect(
            host='_{{DB_HOST}}_',
            user='_{{DB_USER}}_',
            password='_{{DB_PASSWORD}}_',
            db=('supplier' if db == 'supplier' else 'mall'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        # conn = pymysql.connect(
        #     host='localhost',
        #     user='root',
        #     password='123456',
        #     db='test',
        #     charset='utf8mb4',
        #     cursorclass=pymysql.cursors.DictCursor
        # )
        return conn
    except Exception as e:
        return e


"""
 查询表

"""
def search_tb(conn, sql):
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(e)


"""
 插入表
"""
def insert_tb(conn, sql):
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print('insert', e)


"""
 更新表
"""
def update_tb(conn, sql):
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            conn.commit()
    except Exception as e:
        print('update', e)


def get_table_column(tb_name, conn):
    sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}'".format(tb_name)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            f_all = cursor.fetchall()
            return set([x['COLUMN_NAME'] for x in f_all])
    except Exception as e:
        print(e)


def remove_table_column_name(column_names, names):
    for name in names:
        if name in column_names:
            column_names.remove(name)
    return ', '.join(column_names)


def back_keys(keys):
    s1 = ''
    for index, key in enumerate(keys):
        if index == len(keys) - 1:
            s1 += '`{}`'.format(key)
        else:
            s1 += '`{}`, '.format(key)
    return s1


def back_set_value(d, hide_name):
    set_value = ''
    for k, v in d.items():
        if k in hide_name:
            continue
        set_value += "`{}`=\'{}\', ".format(k, v)
    return set_value[:-2]


#关闭数据库
def close_database(conn):
    conn.close()


"""
更新use表数据库
 1.根据原始id查找
 2.根据目标id查找
 3.如果存在目标记录更新，否则新建
"""
def update_users_table(conn, origin_name, purpose_name, table_name):
    search_origin_sql = "SELECT * FROM {} WHERE `username`='{}'".format(table_name, origin_name)
    search_origin_results = search_tb(conn, search_origin_sql)
    if search_origin_results:
        origin_dic = search_origin_results[0]
        origin_id = origin_dic['uid']
        # 查询 sdb_user_supplier 是否存在新的id
        # 如果存在就更新这条数据
        # 如果不存在插入这条数据
        search_sql = "SELECT * FROM {} WHERE `username`='{}'".format(table_name, purpose_name)
        search_purpose_results = search_tb(conn, search_sql)
        if search_purpose_results:
            purpose_id = search_purpose_results[0]['uid']
            # origin_dic['username'] = purpose_name
            # update
            # set_value = back_set_value(origin_dic, ['uid', 'username', 'password'])
            # update_sql = "UPDATE {} SET {} WHERE `username`='{}'".format(table_name, set_value, purpose_name)
            # update_tb(conn, update_sql)
            return (origin_id, purpose_id)
        else:
            # raise Exception('用户名错误，请查看')
            return (False, False)
    else:
        # raise Exception('用户名错误，请查看')
        return (False, False)


"""
更新goods数据表
"""
def update_goods_table(conn, origin_id, purpose_id, table_name):
    search_sql = "SELECT * FROM {} WHERE `company_id`={}".format(table_name, origin_id)
    search_result = search_tb(conn, search_sql)
    if len(search_result) > 0:
        # zgoods_ids 记录新插入条的id
        zgoods_ids = []
        # goods_ids 记录查询出来原有的id
        goods_ids = []
        for d in search_result:
            #这两种情况我并不考虑
            if d['disabled'] == 'true':
                continue
            d['is_check'] = 0
            d['is_oper'] = 0
            goods_ids.append(d['goods_id'])
            del d['goods_id']
            d['company_id'] = purpose_id
            insert_sql = "INSERT INTO {} ({}) VALUES {}".format(table_name, back_keys(d.keys()), tuple(d.values()))
            insert_sql = insert_sql.replace('None', 'NULL')
            insert_sql = insert_sql.replace('Decimal', '')
            new_id = insert_tb(conn, insert_sql)
            zgoods_ids.append(new_id)
            image_default = d['image_default']
            update_goods(conn, default_images_id=image_default, new_goods_id=new_id)
        return zgoods_ids, goods_ids


"""
更新supplier中goods_ids表
"""
def update_product_table(conn, goods_ids, zgoods_ids, table_name):
    # all_zproduct_ids = []
    # all_product_ids = []
    out_index = 0
    index = 0
    for old_id, new_id in zip(goods_ids, zgoods_ids):
        search_sql = "SELECT * FROM {} WHERE `goods_id`={}".format(table_name, old_id)
        search_result = search_tb(conn, search_sql)
        product_ids = []
        # zproduct_ids = []
        out_index += 1
        for d in search_result:
            product_ids.append(d['product_id'])
            del d['product_id']
            d['goods_id'] = new_id
            insert_sql = "INSERT INTO {} ({}) VALUES {}".format(table_name, back_keys(d.keys()), tuple(d.values()))
            insert_sql = insert_sql.replace('None', 'NULL')
            insert_sql = insert_sql.replace('Decimal', '')
            insert_tb(conn, insert_sql)
            index += 1
        # all_product_ids.append(product_ids)
        # all_zproduct_ids.append(zproduct_ids)
    # return all_zproduct_ids


# """
# 更新mall中的good表
# """
# def update_mall_goods_table(conn, origin_id, purpose_id, goods_ids, zgoods_ids, table_name):
#     search_sql = "SELECT * FROM {} WHERE `company_id`={}".format(table_name, origin_id)
#     search_result = search_tb(conn, search_sql)
#     mall_goods_id = []
#     mall_zgoods_id = []
#     if len(search_result) > 0:
#         for d in search_result:  #zgoods_id zgoods_ids
#             if d['disabled'] == 'true':
#                 continue
#             z_id = d['zgoods_id']
#             index = goods_ids.index(z_id)
#             mall_goods_id.append(d['goods_id'])
#             del d['goods_id']
#             d['company_id'] = purpose_id
#             d['zgoods_id'] = zgoods_ids[index]
#             insert_sql = "INSERT INTO {} ({}) VALUES {}".format(table_name, back_keys(d.keys()), tuple(d.values()))
#             insert_sql = insert_sql.replace('None', 'NULL')
#             insert_sql = insert_sql.replace('Decimal', '')
#             mall_zgoods_id.append(insert_tb(conn, insert_sql))
#         return mall_zgoods_id, mall_goods_id
#     else:
#         # raise Exception('查找origin_goods表失败')
#         return ('查找origin_goods表失败', '查找origin_goods表失败')
#
#
# """
# 更新mall中的product表
# """
# def update_mall_product_table(conn, goods_ids, zgoods_ids, table_name):  #zproduct_ids
#     sup_conn = connect_database('supplier')
#     index = 0
#     out_index = 0
#     zproduct_ids = []
#     for old_id, new_id in zip(goods_ids, zgoods_ids): #product_ids zproduct_ids
#         search_sql = "SELECT * FROM {} WHERE `goods_id`={}".format(table_name, old_id)
#         search_result = search_tb(conn, search_sql)
#         search_mall_goodsTB_sql = "SELECT * FROM {} WHERE `goods_id`={}".format('sdb_goods', new_id)
#
#         res = search_tb(conn, search_mall_goodsTB_sql)
#         if res:
#             res_id = res[0]['zgoods_id']
#             search_sup_productTB_sql = "SELECT * FROM {} WHERE `goods_id`={}".format('sdb_products', res_id)
#             sup_res = search_tb(sup_conn, search_sup_productTB_sql)
#             if sup_res:
#                 zproduct_ids = [x['product_id'] for x in sup_res]
#         out_index += 1
#
#         for d, zproduct_id in zip(search_result, zproduct_ids):
#             del d['product_id']
#             d['goods_id'] = new_id
#             d['zproduct_id'] = zproduct_id
#             insert_sql = "INSERT INTO {} ({}) VALUES {}".format(table_name, back_keys(d.keys()), tuple(d.values()))
#             insert_sql = insert_sql.replace('None', 'NULL')
#             insert_sql = insert_sql.replace('Decimal', '')
#             insert_tb(conn, insert_sql)
#             index += 1
#     sup_conn.close()

"""
更新gimages_table
"""
def update_gimage_table(conn, default_images_id, new_goods_id):
    columns = remove_table_column_name(get_table_column('sdb_gimages', conn), ['gimage_id'])
    gimage_sql = "SELECT * FROM sdb_gimages WHERE goods_id=(SELECT goods_id FROM sdb_gimages WHERE gimage_id='{}')".format(default_images_id)
    select_results = search_tb(conn, gimage_sql)
    isReturn = False
    last_num = 0
    for select_result in select_results[::-1]:
        # print(select_result['gimage_id'])
        isReturn = True if str(select_result['gimage_id']) == default_images_id else False
        del select_result['gimage_id']
        select_result['goods_id'] = new_goods_id
        insert_sql = 'INSERT INTO {} ({}) VALUES {}'.format('sdb_gimages', back_keys(select_result.keys()), tuple(select_result.values()))
        insert_sql = insert_sql.replace('None', 'NULL')
        insert_sql = insert_sql.replace('Decimal', '')
        num = insert_tb(conn, insert_sql)
        if isReturn:
             last_num = num
    return last_num


"""
更新 goods_table image_default
"""
def update_goods(conn, default_images_id, new_goods_id):
    last_num = update_gimage_table(conn, default_images_id, new_goods_id)
    update_sql = "UPDATE {} SET image_default={} WHERE goods_id={}".format('sdb_goods', last_num, new_goods_id)
    update_sql = update_sql.replace('None', 'NULL')
    update_sql = update_sql.replace('Decimal', '')
    update_tb(conn, update_sql)


def changedb(origin_name, purpose_name):
    try:
        conn = connect_database('supplier')
    except Exception as e:
        print(e)
    if conn:
        # 更新users表数据表
        origin_id, purpose_id = update_users_table(conn, origin_name, purpose_name, 'sdb_users')
        if origin_id and purpose_id:
            # 更新goods表
            zgoods_ids, goods_ids = update_goods_table(conn, origin_id, purpose_id, 'sdb_goods')
            # 更新Supplier中product表
            update_product_table(conn, goods_ids, zgoods_ids, 'sdb_products')  # zproduct_ids =
            conn.close()
            return ''
            # if len(zgoods_ids) > 0:
            #     conn = connect_database()
            #     # 更新mall中的goods表
            #     mall_zgoods_ids, mall_goods_ids = update_mall_goods_table(conn, origin_id, purpose_id, goods_ids,
            #                                                               zgoods_ids, 'sdb_goods')
            #     # 更新mall中的product表
            #     update_mall_product_table(conn, mall_goods_ids, mall_zgoods_ids, 'sdb_products')  # zproduct_ids,
            #     # print('更新完成~！')
            #     conn.close()
            #     return True
            # else:
            #     # print('更新完成~！')
            #     return True
        else:
            conn.close()
            # raise Exception('查找users表失败')
            return '查找users表失败'
    else:
        # raise Exception('链接数据库失败')
        return '链接数据库失败'


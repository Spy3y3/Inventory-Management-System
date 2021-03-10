from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "\xf6!\x06\xc1\xe50%\x8c\xf1\xb4\x8e/S\xdf"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'inventory'

mysql = MySQL(app)


@app.route('/')
def root():
    return redirect(url_for('index'))


@app.route("/index")
def index():
    return render_template('index.html')


@app.route("/product")
def product():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM product")
    data = cur.fetchall()
    cur.close()
    return render_template('product.html', product=data)


@app.route('/addproduct', methods=['POST'])
def addproduct():
    if request.method == "POST":
        flash("Your Product has been Added!")
        pn = request.form['pn']
        pd = request.form['pd']
        pq = request.form['pq']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO product (ProductName, ProductDescription, Quantity) VALUES (%s, %s, %s)", (pn, pd, pq))
        mysql.connection.commit()
        return redirect(url_for('product'))


@app.route('/updateproduct', methods=['POST', 'GET'])
def updateproduct():
    if request.method == 'POST':
        id_data = request.form['id']
        pn = request.form['pn']
        pd = request.form['pd']
        pq = request.form['pq']
        cur = mysql.connection.cursor()
        cur.execute("""SELECT * FROM product WHERE ProductID=%s""", (id_data,))
        prod = cur.fetchone()
        cur.execute("UPDATE product SET ProductName=%s, ProductDescription=%s, Quantity=%s WHERE ProductID=%s",
                    (pn, pd, pq, id_data))
        cur.execute(""" SELECT  * FROM balance WHERE produc =%s""", (prod[1],))
        bal = cur.fetchone()
        if bal:
            cur.execute("""UPDATE balance SET produc= %s WHERE ID= %s""", (pn, bal[0]))
            cur.execute("""UPDATE movement SET ProductName= %s WHERE ProductName= %s""", (pn, prod[1]))
        flash("Your Product has been Updated!")
        mysql.connection.commit()
        return redirect(url_for('product'))


@app.route('/deleteproduct/<string:id_data>', methods=['GET'])
def deleteproduct(id_data):
    flash("Your Product has been Deleted!")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM product WHERE ProductID=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('product'))


@app.route("/location")
def location():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM location")
    data = cur.fetchall()
    cur.close()
    return render_template('location.html', location=data)


@app.route('/addlocation', methods=['POST'])
def addlocation():
    if request.method == "POST":
        flash("Your Location has been Added!")
        ln = request.form['ln']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO location (LocationName) VALUES (%s)", (ln,))
        mysql.connection.commit()
        return redirect(url_for('location'))


@app.route('/updatelocation', methods=['POST', 'GET'])
def updatelocation():
    if request.method == 'POST':
        id_data = request.form['id']
        ln = request.form['ln']
        cur = mysql.connection.cursor()
        cur.execute("""SELECT * from location WHERE LocationID = %s """, (id_data,))
        loc = cur.fetchone()
        cur.execute("""
               UPDATE location
               SET LocationName=%s WHERE LocationID=%s """, (ln, id_data))
        cur.execute(""" SELECT  * FROM balance WHERE location =%s""", (loc[1],))
        bal = cur.fetchone()
        if bal:
            cur.execute("""UPDATE balance SET location= %s WHERE ID= %s""", (ln, bal[0]))
            cur.execute("""UPDATE movement SET FromLocation= %s WHERE FromLocation= %s""", (ln, loc[1]))
            cur.execute("""UPDATE movement SET ToLocation= %s WHERE ToLocation= %s""", (ln, loc[1]))
        flash("Your Product has been Updated!")
        mysql.connection.commit()
        return redirect(url_for('location'))


@app.route('/deletelocation/<string:id_data>', methods=['GET'])
def deletelocation(id_data):
    flash("Your Location has been Deleted!")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM location WHERE LocationID=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('location'))


@app.route("/movement")
def movement():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM movement")
    movement = cur.fetchall()

    cur.execute("SELECT  * FROM product")
    pro = cur.fetchall()

    cur.execute("SELECT  * FROM location")
    loc = cur.fetchall()
    cur.close()
    context = {
        'movement': movement,
        'pro': pro,
        'loc': loc
    }

    return render_template('movement.html', **context)


@app.route('/addmovement', methods=['POST'])
def addmovement():
    if request.method == "POST":
        pn = request.form['pn']
        fl = request.form['fl']  # from (Source)
        tl = request.form['tl']  # to (destination)
        pq = request.form['pq']  # product quantity
        # dt = request.form['dt']
        cur = mysql.connection.cursor()
        import datetime
        dt = datetime.datetime.now()
        boolbeans = check(fl, tl, pn, pq)
        if boolbeans == False:
            flash(f'Retry with lower quantity than source location', 'danger')
        elif boolbeans == 'same':
            flash(f'Source and destination cannot be the same.', 'danger')
        elif boolbeans == 'no prod':
            flash(f'Not enough products in this loaction .Please add products', 'danger')
        else:
            cur.execute(
                "INSERT INTO movement (ProductName, FromLocation, ToLocation, DateTiming, Quantity) VALUES (%s, "
                "%s, %s, %s, %s)", (pn, fl, tl, dt, pq))
            mysql.connection.commit()
            flash("Your Product has been Moved!")
        return redirect(url_for('movement'))


@app.route('/updatemovement', methods=['POST', 'GET'])
def updatemovement():
    if request.method == 'POST':
        id_data = request.form['id']
        pn = request.form['pn']
        fl = request.form['fl']
        tl = request.form['tl']
        pq = request.form['pq']
        dt = request.form['dt']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE movement
               SET ProductName=%s, FromLocation=%s, ToLocation=%s, DateTiming=%s, Quantity=%s WHERE MovementID=%s """,
                    (pn, fl, tl, pq, dt, id_data))
        flash("Your Product has been Updated!")
        mysql.connection.commit()
        return redirect(url_for('movement'))


@app.route('/deletemovement/<string:id_data>', methods=['GET'])
def deletemovement(id_data):
    flash("Your Move Product has been Deleted!")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM movement WHERE MovementID=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('movement'))


@app.route("/stockreport")
def stockreport():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM product")
    data = cur.fetchall()
    cur.close()
    return render_template('stockreport.html', stockreport=data)


def check(frm, to, name, qty):
    qty = int(qty)
    if frm == to:
        a = 'same'
        return a
    elif frm == 'Warehouse' and to != 'Warehouse':
        cur = mysql.connection.cursor()
        cur.execute(""" SELECT  * FROM product WHERE ProductName= %s""", (name,))
        prodq = cur.fetchone()
        print(prodq[3])
        if prodq[3] >= qty:
            prod_qty = prodq[3] - qty
            cur.execute("""UPDATE product SET Quantity= %s WHERE ProductID= %s""", (prod_qty, prodq[0]))
            cur.execute("""SELECT  * FROM balance WHERE produc =%s AND location= %s""", (name, to))
            bal = cur.fetchone()
            a = str(bal)
            if (a == 'None'):
                new = cur.execute("""INSERT INTO balance (produc, location, quantity) VALUES (%s, %s, %s)""",
                                  (name, to, qty))
                mysql.connection.commit()
            else:
                qty = bal[3] + qty
                cur.execute("""UPDATE balance SET quantity= %s WHERE ID= %s""", (qty, bal[0]))
            mysql.connection.commit()
        else:
            return False
    elif to == 'Warehouse' and frm != 'Warehouse':

        cur.execute("""SELECT  * FROM balance WHERE produc =%s AND location= %s""", (name, frm))
        bal = cur.fetchone()
        a = str(bal)
        if (a == 'None'):
            return 'no prod'
        else:
            if bal[3] >= qty:
                cur.execute("""SELECT  * FROM product WHERE ProductName =%s""", (name,))
                prodq = cur.fetchone()

                prod_qty = prodq[3] + qty
                cur.execute("""UPDATE product SET Quantity= %s WHERE ProductID= %s""", (prod_qty, prodq[0]))

                qty = bal[3] - qty
                cur.execute("""UPDATE balance SET quantity= %s WHERE ID= %s""", (qty, bal[0]))

                mysql.connection.commit()

            else:
                return False

    else:  # from='?' and to='?'
        cur = mysql.connection.cursor()
        cur.execute("""SELECT  * FROM balance WHERE produc =%s AND location= %s""",
                    (name, frm))  # check if from location is in Balance
        bl = cur.fetchone()
        a = str(bl)
        if (a == 'None'):  # if not
            return 'no prod'

        elif (bl.quantity - 100) > qty:
            # if from qty is sufficiently large, check to  in Balance
            cur.execute("""SELECT  * FROM balance WHERE produc =%s AND location= %s""", (name, to))
            bal = cur.fetchone()
            a = str(bal)
            if a == 'None':
                # if not add entry
                new = cur.execute("""INSERT INTO balance (produc, location, quantity) VALUES (%s, %s, %s)""",
                                  (name, to, qty))
                mysql.connection.commit()

                cur.execute("""SELECT  * FROM balance WHERE produc =%s AND location= %s""", (name, frm))
                bal = cur.fetchone()
                qty = bal[3] - qty
                cur.execute("""UPDATE balance SET quantity= %s WHERE ID= %s""", (qty, bal[0]))
                mysql.connection.commit()
            else:  # else add to 'from' qty and minus from 'to' qty
                # if yes,add to to qty

                cur.execute("""SELECT  * FROM balance WHERE produc =%s AND location= %s""", (name, frm))
                bl = cur.fetchone()
                qty = bl[3] - qty
                cur.execute(""" UPDATE balance SET quantity= %s WHERE ID= %s """, (qty, bal[0]))
                mysql.connection.commit()
        else:
            return False


if __name__ == '__main__':
    app.run(debug=True)

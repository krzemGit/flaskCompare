from comparator import app, db
from comparator.common_oop import Amazon, Ebay, Allegro
from comparator.forms import First_search 
from comparator.models import Search, Result
from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash, jsonify


# homepage
@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
    form = First_search()
    return render_template('home.html', form=form, template_name='home')


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', template_name='about')


@app.route('/results/', methods=['GET'])
def results():
    ''' MAIN ROUTE: displays results after searching, saving results handled by '/save' route'''
    phrase = request.args.get('phrase')
    amazon = request.args.get('amazon')
    ebay = request.args.get('ebay')
    allegro = request.args.get('allegro')
    trans_phrase = None
    results = []
    platforms = []

    searches = Search.query.all()
    for search in searches:
        print(search.get_platforms())

    # adding results from particular platforms
    if amazon:
        platforms.append('amazon')
        amazon_list = Amazon(phrase)
        results.extend(amazon_list.search_list)
    if ebay:
        platforms.append('ebay')
        ebay_list = Ebay(phrase)
        results.extend(ebay_list.search_list)
    if allegro:
        platforms.append('allegro')
        allegro_list = Allegro(phrase)
        results.extend(allegro_list.search_list)
        trans_phrase = allegro_list.phrase

    # formatting info about the platforms for display
    if len(platforms) > 0:
        platforms = ', '.join(platforms)
    else:
        platforms = 'no platform was chosen'

    return render_template('results.html', phrase=phrase, trans_phrase=trans_phrase, platforms=platforms, amazon=amazon, ebay=ebay, allegro=allegro, results=results, searches=searches)


@app.route('/save', methods=['POST'])
def save():
    ''' JSON route, for adding results to database and create saves, returns JSON
    codes: 200, 400, 408, 409, 410, 501
     '''
    if request.method == 'POST':

        # data
        posted_data = request.get_json()
        search = posted_data.get('search')
        result = posted_data.get('result')

        # list for a successful message
        msg = []

        # initial validation
        all_searches = len(Search.query.all())
        all_results = len(Result.query.all())

        if all_searches >= 100 or all_results >= 100:
            res_json = {'status': 'failure', 'code': 410, 'msg': 'Too may records in the database'}
            return jsonify(res_json)

        # write data to database
        if posted_data.get('newSearch'):
            # validation for search 
            if search['searchTitle'] == None or len(search['searchTitle']) < 2:
                res_json = {'status': 'failure', 'code': 409, 'msg': 'Search Title not given or it is too short'}
                return jsonify(res_json)

            add_search = Search(username=search['username'] , search_title=search['searchTitle'])
            db.session.add(add_search)
            msg.append('Search successfully added to the database!')
        elif not posted_data.get('newSearch'):
            add_search = Search.query.filter_by(id=search["id"]).first()

            # validation - no two similar results in one search and no more than 45 results per search
            if len(add_search.results) > 45:
                res_json = {'status': 'failure', 'code': 501, 'msg': 'Too many results for this search, please create a new search to store this result'}
                return jsonify(res_json)

            for item in add_search.results:
                if item.title == result['title']:
                    res_json = {'status': 'failure', 'code': 501, 'msg': 'This result already added to this search'}
                    return jsonify(res_json)
        else:
            res_json = {'status': 'failure', 'code': 408, 'msg': 'Search not defined, please check your form'}
            return jsonify(res_json)

        # adding result
        new_result = Result(platform=result['platform'], phrase=result['phrase'], title=result['title'], link=result['link'], image=result['image'], price_info=result['price'],search=add_search)
        db.session.add(new_result)
        db.session.commit()
        msg.append('Result successfully added to the database!')
        msg = '\n'.join(msg)

        res = {'status': 'success', 'code': 200, 'msg': msg}
    
    # response for a different method
    else: 

        res = {'status': 'failure', 'code': 400, 'msg': 'Method not allowed'}

    return jsonify(res)


@app.route('/clear')
def clear():
    ''' This route clears the database if the limit of 20 searches has been exceeded '''
    searches = Search.query.order_by(Search.search_date.desc()).all()

    searches = searches[10:]
    ids = [i.id for i in searches]
    print(ids)
    
    for ident in ids:
        Result.query.filter_by(search_id=ident).delete()
        Search.query.filter_by(id=ident).delete()
    
    db.session.commit()
    if len(ids) > 0:
        flash('Database cleared to last 10 searches!')
    else: 
        flash('Database is not full, no records were deleted')
    return redirect(url_for('home'))


@app.route('/saved-results', methods=['GET'])
def saved_results():
    ''' route for displaying saved results '''
    template_name = 'reload'
    search_id = int(request.args.get('id', 0))
    searches = Search.query.all()
    results = Result.query.filter_by(search_id=search_id).all()

    print(results)

    return render_template('saved_results.html',
                            search_id=search_id, 
                            searches=searches, 
                            results=results, 
                            template_name=template_name)
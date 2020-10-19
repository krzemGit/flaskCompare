from comparator import app, db
from comparator.common import (translate_to_polish, 
                    amazon_search, 
                    ebay_search, 
                    allegro_search, 
                    session_results, 
                    create_id)
from comparator.forms import First_search 
from comparator.models import Search, Result
from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash


# homepage
@app.route('/', methods=['POST','GET'])
@app.route('/home', methods=['POST','GET'])
def home():
    form = First_search()
    return render_template('home.html', form=form, template_name='home')


# main view of results - the longest route
@app.route('/results/', methods=['GET', 'POST'])
def results():
    # save resutls to database
    if request.method == 'POST':
        searches = Search.query.all()
        if len(searches) == 0:
            id = 1
        elif len(searches) <= 20:
            id = create_id(searches)
        else:
            return render_template('saved.html', db_full=True)
        name = request.form.get('your-name')
        submit_date = datetime.utcnow()
        search_title = request.form.get('search-title', 'no title')
        sphrase = session.get('sphrase', None)
        strans_phrase = session.get('stransphrase', None)
        sresults = session.get('sresults', None)
        res_no = len(sresults)
        phrase = f'<span id="phrase">{sphrase}</span><span class="trans-phrase"> (pol. {strans_phrase})</span>'
       
        db.session.add(Search(id=id , username=name , search_title=search_title , phrase=phrase))
        db.session.commit()

        for item in sresults:
            db.session.add(Result(search_id=id ,
                                  platform=item['platform'],
                                  title=item['title'],
                                  link=item['link'],
                                  image=item['image'],
                                  price_info=list(item['price'])))
            db.session.commit()

        session.clear()

        return render_template('saved.html', submit_date=submit_date, title=search_title, phrase=phrase, res_no=res_no, db_full=False)

    # displays results after webscrapping
    elif request.method == 'GET':
        phrase = request.args.get('phrase')
        amazon = request.args.get('amazon')
        ebay = request.args.get('ebay')
        allegro = request.args.get('allegro')
        trans_phrase = translate_to_polish(phrase)
        results = []
        if amazon:
            results.extend(amazon_search(phrase))
        if ebay:
            results.extend(ebay_search(phrase))
            print(ebay_search(phrase))
        if allegro:
            results.extend(allegro_search(trans_phrase))
        session['sphrase'] = phrase
        session['stransphrase'] = trans_phrase
        session['sresults'] = session_results(results)
        return render_template('results.html', phrase=phrase, pol_phrase=trans_phrase, amazon=amazon, ebay=ebay, allegro=allegro, results=results)


# clears the database - limits the searches to the last 10 searches
@app.route('/clear')
def clear():
    searches = Search.query.order_by(Search.search_date.desc()).all()

    searches = searches[10:]
    ids = [i.id for i in searches]
    print(ids)
    
    for ident in ids:
        Result.query.filter_by(search_id=ident).delete()
        Search.query.filter_by(id=ident).delete()
    
    db.session.commit()

    flash('Database cleared to last 10 searches!')
    return redirect(url_for('home'))

# routs for displaying saved results with Ajax
@app.route('/ajax-results', methods=['GET', 'POST'])
def ajax_results():
    template_name = 'ajax'

    search_id = 0
    searches = Search.query.all()
    results = Result.query.filter_by(search_id=search_id).all()
    platforms = ['amazon', 'ebay', 'allegro']

    return render_template('saved_results.html', 
                            search_id=search_id, 
                            searches=searches, 
                            results=results, 
                            platforms=platforms, 
                            template_name=template_name)

@app.route('/ajax-request', methods=['GET', 'POST'])
def ajax_request():
    search_id = request.args.get('id', 0)
    search_id = int(search_id)
    search = Search.query.filter_by(id=search_id).first()
    results = Result.query.filter_by(search_id=search_id).all()
    platforms = ['amazon', 'ebay', 'allegro']

    return render_template('display_saved_ajax.html', results=results, search=search, platforms=platforms)


# routs for displaying saved results with redirects (GET method)
@app.route('/saved-results', methods=['GET'])
def saved_results():
    template_name = 'reload'
    search_id = request.args.get('id', 0)
    search_id = int(search_id)
    searches = Search.query.all()
    results = Result.query.filter_by(search_id=search_id).all()
    platforms = ['amazon', 'ebay', 'allegro']

    return render_template('saved_results.html', 
                            search_id=search_id, 
                            searches=searches, 
                            results=results, 
                            platforms=platforms, 
                            template_name=template_name)
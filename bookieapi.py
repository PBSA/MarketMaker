import json
from flask import Flask
from flask import request
from flask import Response
from flask import make_response
from flask import jsonify
from flask import make_response
from peerplays import PeerPlays
from peerplaysbase import operations
from peerplays.amount import Amount
from peerplays.account import Account
from peerplays.exceptions import *
import bookie
import time

app = Flask(__name__)
ppy = PeerPlays(nobroadcast=True)
ppy.wallet.unlock(bookie.pwd)

#Bookie related calls

@app.route("/placeBets", methods=['POST'])
def placeBets():
	try:
		account = request.args.get("account")
		body = request.get_json()
		response = []
		for bet in body:
			asset_symbol = bet['asset_symbol']
			bet_amount = bet['bet_amount']
			betting_market_id = bet['betting_market_id']
			odds = bet['odds']
			back_or_lay = bet['back_or_lay']
			a  = Amount(bet_amount, asset_symbol)
			#right now, we will place bets successfully one by one until one breaks.
			#the user will be confused whether any of the bets got placed or not
			bet_response = ppy.bet_place(betting_market_id, a, odds, back_or_lay, account, fee_asset = asset_symbol)
			response.append(bet_response)
		return jsonify(response)
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

@app.route("/placeSingleBet", methods=['POST'])
def placeSingleBet():
	try:
		accountStr = request.args.get("account")
		account = Account(accountStr, peerplays_instance = ppy, full=True)
		print(accountStr)
		body = request.get_json()
		asset_symbol = body['asset_symbol']
		bet_amount = body['bet_amount']
		betting_market_id = body['betting_market_id']
		odds = body['odds']
		back_or_lay = body['back_or_lay']
		a  = Amount(bet_amount, asset_symbol)
		#right now, we will place bets successfully one by one until one breaks.
		#the user will be confused whether any of the bets got placed or not
		ppy.bet_place(betting_market_id, a, odds, back_or_lay, account['id'], fee_asset = asset_symbol)
		time.sleep(3) # until next block is produced
		unmatchedBets = bookie.getUnmatchedBets(account['id'])
		if unmatchedBets[-1]['betting_market_id'] == betting_market_id:
			return jsonify(unmatchedBets[-1])
		else:
			matchedBets = bookie.getMatchedBets(account['id'])
			return jsonify(matchedBets[0])
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

@app.route("/bets/<bet_id>", methods=['DELETE'])
def cancelBets(bet_id):
	try:
		# TODO cancel by event id, bmg id
		account = request.args.get("account")
		cancel_response = ppy.bet_cancel(bet_id, account)
		return jsonify(cancel_response)
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

@app.route("/bettors/<bettor_id>/unmatchedBets", methods=['GET'])
def getUnmatchedBets(bettor_id):
	try:
		a = Account(bettor_id, peerplays_instance=ppy, full=True)
		return jsonify(bookie.getUnmatchedBets(a['id']))
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

@app.route("/bettors/<bettor_id>/matchedBets", methods=['GET'])
def getMatchedBets(bettor_id):
	try:
		a = Account(bettor_id, peerplays_instance=ppy, full=True)
		return jsonify(bookie.getMatchedBets(a['id']))
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

@app.route("/sports", methods=['GET'])
def getSports():
	try:
		return jsonify(bookie.getSports())
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

@app.route("/sports/<sport_id>/eventGroups", methods=['GET'])
def getEventGroups(sport_id):
	try:
		return jsonify(bookie.getEventGroups(sport_id))
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

@app.route("/eventGroups/<event_group_id>/events", methods=['GET'])
def getEvents(event_group_id):
	try:
		return jsonify(bookie.getEvents(event_group_id))
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

@app.route("/events/<event_id>/bettingMarketGroups", methods=['GET'])
def getBettingMarketGroups(event_id):
	try:
		return jsonify(bookie.getBettingMarketGroups(event_id))
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

@app.route("/bettingMarketGroups/<bmg_id>/bettingMarkets", methods=['GET'])
def getBettingMarkets(bmg_id):
	try:
		return jsonify(bookie.getBettingMarkets(bmg_id))
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

@app.route("/rules/<rules_id>", methods=['GET'])
def getRules(rules_id):
	try:
		return jsonify(bookie.getRules(rules_id))
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

#Other calls

@app.route("/bettors/<bettor_id>/history", methods=['GET'])
def getHistory(bettor_id):
	try:
		try:
			limit = int(request.args['limit'])
		except:
			limit = 10
		print(limit)
		return jsonify(bookie.getHistory(bettor_id,limit))
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

@app.route("/bettors/<bettor_id>/accountDetails", methods=['GET'])
def getAccountDetails(bettor_id):
	try:
		return jsonify(bookie.getAccountDetails(bettor_id))
	except Exception as e:
		return make_response(jsonify(error=e.__doc__), 500)

if __name__ == '__main__':
	app.run(debug=False, host='0.0.0.0', port=5051)

def email_creation(name,
                    p_type,
                    date_range,
                    member_count,
                    p_category,
                    star_score,
                    extreme_count,
                    visit_reason,
                    positive_topic,
                    negative_topic):
    loop_stars = """"""
    visit_reason_loop = """"""
    positive_topic_loop = """"""
    negative_topic_loop = """"""

    text = """<!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8" /> <meta http-equiv="X-UA-Compatible" content="IE=edge" /> <meta name="viewport" content="width=device-width, initial-scale=1.0" /> <title>Everside</title> </head> <body style="width: 626px; margin-left: auto; margin-right: auto;"> <div style=" background-color: #33B1AB; width: 618px; padding-right: 5px; padding-left: 3px; padding-bottom: 10px; padding-top: 10px; border-radius: 10px; "> <div     style=" background-color: #eef6f4; width: 600px; margin-left: auto; margin-right: auto; padding: 10px; border-radius: 10px; "> <table style="width: 100%"> <tr style="width: 100%"> <td style="width: 200px; padding: 30px 0; text-align: center"> <img src="https://i.ibb.co/4gfQdrj/everside-logo.png" alt="everside-logo" style="width: 200px" /> </td> </tr> </table> <table style=" width: 100%; text-align: center; margin-left: auto; margin-right: auto; " > <tr> <td style=" width: 70%; color: #0da19a; font-size: 35px; font-weight: 500; text-align: left; vertical-align: bottom; " > {name} </td> <td style=" width: 20%; vertical-align: bottom; " > <h1 style=" background-color: white; color: rgba(0, 0, 0, 0.548); border-radius: 10px 0px 0px 10px; padding: 5px; font-size: 16px; font-weight: 400; " > Type </h1> </td> <td style=" width: 10%; vertical-align: bottom; " > <h1 style=" text-align: center; background-color: #e9fffe; color: #0da19a; font-weight: 600; font-size: 16px; border-radius: 0px 10px 10px 0px; margin-right: 10px; padding: 5px; " > {p_type} </h1> </td> </tr> </table> <table style=" width: 100%; text-align: center; margin-left: auto; margin-right: auto; margin-bottom: 10px; " > <tr> <td style="width: 35%"> <h1 style=" background-color: white; color: rgba(0, 0, 0, 0.548); border-radius: 10px; font-size: 16px; font-weight: 400; padding: 5px; margin-right: 10px; " > {date_range} </h1> </td> <td style="width: 25%"> <h1 style=" background-color: white; color: rgba(0, 0, 0, 0.548); border-radius: 10px 0px 0px 10px; padding: 5px; font-size: 16px; font-weight: 400; " > No. of Patients </h1> </td> <td style="width: 10%"> <h1 style=" text-align: center; background-color: #e9fffe; color: #0da19a; font-weight: 600; font-size: 16px; border-radius: 0px 10px 10px 0px; margin-right: 10px; padding: 5px; " > {member_count} </h1> </td> <td style=" width: 20%; " > <h1 style=" background-color: white; color: rgba(0, 0, 0, 0.548); border-radius: 10px 0px 0px 10px; padding: 5px; font-size: 16px; font-weight: 400; " > Category </h1> </td> <td style=" width: 10%; " > <h1 style=" text-align: center; background-color: #e9fffe; color: #0da19a; font-weight: 600; font-size: 16px; border-radius: 0px 10px 10px 0px; margin-right: 10px; padding: 5px; " > {p_category} </h1> </td> </tr> </table> <table cellspacing="0" cellpadding="0" style="margin-bottom: 10px; width: 100%" > <tr> {loop_stars} </tr> </table> <table   style=" width: 100%; text-align: center; margin-left: auto; margin-right: auto; margin-bottom: 10px; "> <tr "> <td style=" width: 80%; background-color: white; color: #2dafa9; border-radius: 10px 0px 0px 10px; text-align: left; font-weight: 600; padding: 10px;">YOUR SCORE</td> <td style="     width: 20%; text-align: center; background-color: #e9fffe; color: #0da19a; font-weight: 600; font-size: 25px; border-radius: 0px 10px 10px 0px; padding: 10px;">{star_score}</td> </tr> </table> <table   style=" width: 100%; text-align: center; margin-left: auto; margin-right: auto; margin-bottom: 10px; "> <tr class=""> <td style="      width: 80%; background-color: white; color: #2dafa9; border-radius: 10px 0px 0px 10px; text-align: left; font-weight: 600; padding-right: 10px; padding-left: 10px; padding-top: 15px; padding-bottom: 15px;">EXTREME COMMENTS</td> <td style="  width: 20%; text-align: center; background-color: #e9fffe; color: #0da19a; font-weight: 600; font-size: 25px; border-radius: 0px 10px 10px 0px; padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px;">{extreme_count}</td> </tr> </table> <table style=" width: 100%; text-align: center; margin-left: auto; margin-right: auto; background-color: white; border-radius: 10px 10px 0 0;"> <tr> <td> <h1 style="  color: #2dafa9; text-align: left; font-size: 16px; font-weight: 600; padding-right: 10px; padding-left: 10px; padding-top: 15px; padding-bottom: 15px;">REASON FOR PATIENT'S VISIT</h1> </td> </tr> </table> <table style="     background-color: white; border-radius: 0px 0px 10px 10px; padding-bottom: 10px; width: 100%; text-align: center; margin-left: auto; margin-right: auto; margin-bottom: 10px; " > <tr> {visit_reason_loop} </tr> </table> <table style=" width: 100%; text-align: center; margin-left: auto; margin-right: auto; background-color: white; border-radius: 10px 10px 0 0;"> <tr> <td> <h1 style="  color: #2dafa9; font-size: 16px; text-align: left; font-weight: 600; padding-right: 10px; padding-left: 10px; padding-top: 15px; padding-bottom: 15px;">TOPICS</h1> </td> </tr> </table> <table style=" width: 100%; text-align: center; margin-left: auto; margin-right: auto; background-color: white;"> <tr> <td><h1 style="     color: #2dafa9; font-weight: 500; padding-right: 10px; padding-left: 10px; padding-top: 15px; padding-bottom: 15px; width: 100%; text-align: center; font-size: 16px;">MOST VALUABLE</h1></td> <td><h1 style="     color: #2dafa9; font-weight: 500; padding-right: 10px; padding-left: 10px; padding-top: 15px; padding-bottom: 15px; width: 100%; text-align: center; font-size: 16px;">LEAST VALUABLE</h1></td> </tr> </table> <table style="     background-color: white; border-radius: 0px 0px 10px 10px; padding-bottom: 30px; width: 100%; text-align: center; margin-left: auto; margin-right: auto; margin-bottom: 30px; " > <tr> <td style="  vertical-align: top; width: 50%;"> {positive_topic_loop} </td> <td style="  vertical-align: top; width: 50%;"> {negative_topic_loop} </td> </tr> </table> </div> </div> </body> </html>"""
    star_td = """<td class="box" style="background-position: center;width: 30px;height: 30px;background-size: 30px 30px;background-image: url(https://i.im.ge/2022/08/17/OSijfK.star.png),linear-gradient(to right, #2dafa9 {}%, #e2e2e2 0%);background-repeat: no-repeat;"></td>"""
    visit_reason_td = """<td ><h1 style="background-color: #65f3ee17;margin: 5px;color: rgba(0, 0, 0, 0.614);padding: 10px;font-size: 12px;">{}</h1></td>"""
    positive_topi_td = """<h1 style="background-color: #65f3ee17;margin: 5px;color: rgba(0, 0, 0, 0.614);padding: 10px;font-size: 12px;">{}</h1>"""
    negative_topic_td = """<h1 style="   background-color: #65f3ee17;margin: 5px;color: rgba(0, 0, 0, 0.614);padding: 10px;font-size: 12px;">{}</h1>"""

    # Star Loop
    n = star_score * 10
    fill = n//10
    n_fill  = n%10
    for i in range(10):
        if i<fill:
            loop_stars = loop_stars + star_td.format("100")
        elif  i==fill:
            loop_stars = loop_stars + star_td.format(str(round(n_fill*10,2)))
        else:
            loop_stars = loop_stars + star_td.format("0")
    
    # Visit Reason Loop
    for i in visit_reason:
        visit_reason_loop = visit_reason_loop + visit_reason_td.format(str(i))

    # Positive Topic Loop
    for i in positive_topic:
        positive_topic_loop = positive_topic_loop + positive_topi_td.format(str(i))

    # Negative topic
    for i in negative_topic:
        negative_topic_loop = negative_topic_loop + negative_topic_td.format(str(i))
    
    text = text.format(name = name,
            p_type = p_type,
            date_range = date_range,
            member_count = member_count,
            p_category = p_category,
            loop_stars = loop_stars,
            star_score = star_score,
            extreme_count = extreme_count,
            visit_reason_loop = visit_reason_loop,
            positive_topic_loop = positive_topic_loop,
            negative_topic_loop = negative_topic_loop)
    return(text)
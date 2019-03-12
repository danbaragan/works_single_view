FROM bmat_webbase

ADD build/web/entrypoint.sh \
    $HOME/bin/

ADD build/web/requirements.txt \
    build/web/requirements.dev.txt \
    $HOME/

# TODO make another image, based on this one, for development
RUN pip install -r requirements.dev.txt

RUN chown -R web:web $HOME

USER $USER
VOLUME ["${HOME}/instance"]
ENTRYPOINT ["entrypoint.sh"]
CMD ["run"]
